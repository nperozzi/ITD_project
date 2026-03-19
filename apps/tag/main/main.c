#include <stdio.h>
#include <string.h>

#include "nvs_flash.h"
#include "esp_log.h"

#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"

#include "host/ble_hs.h"
#include "host/ble_gatt.h"

#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

#define DEVICE_NAME "ESL_TAG_001"   // Namnet som BLE-enheten annonserar med

static const char *TAG = DEVICE_NAME;   // Tagg för loggutskrifter

// UUID för vår egen BLE-tjänst
static const ble_uuid128_t g_service_uuid =
    BLE_UUID128_INIT(0x78, 0x56, 0x34, 0x12,
                     0x34, 0x12,
                     0x34, 0x12,
                     0x34, 0x12,
                     0x34, 0x12, 0x34, 0x12, 0x34, 0x12);

// UUID för vår karakteristik
static const ble_uuid128_t g_char_uuid =
    BLE_UUID128_INIT(0xF0, 0xDE, 0xBC, 0x9A,
                     0x78, 0x56,
                     0x34, 0x12,
                     0x78, 0x56,
                     0x34, 0x12, 0x34, 0x12, 0x34, 0x12);

static const char *g_hello_value = "Hello from ESP32-H2";  // Data som skickas vid read
static uint16_t g_char_handle;     // Handle till karakteristikens värde
static uint8_t own_addr_type;      // BLE-adresstyp som enheten använder

// Funktionsprototyper
static void start_advertising(void);
static int gap_event_cb(struct ble_gap_event *event, void *arg);
static int gatt_chr_access_cb(uint16_t conn_handle,
                              uint16_t attr_handle,
                              struct ble_gatt_access_ctxt *ctxt,
                              void *arg);

// Definition av GATT-serverns tjänst och karakteristik
static const struct ble_gatt_svc_def gatt_svcs[] = {
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,   // Primär tjänst
        .uuid = &g_service_uuid.u,           // Tjänstens UUID
        .characteristics = (struct ble_gatt_chr_def[]) {
            {
                .uuid = &g_char_uuid.u,              // Karakteristikens UUID
                .access_cb = gatt_chr_access_cb,     // Callback vid åtkomst
                .flags = BLE_GATT_CHR_F_READ,        // Endast läsbar
                .val_handle = &g_char_handle,        // Spara handle här
            },
            { 0 }   // Slutmarkering
        },
    },
    { 0 }   // Slutmarkering för tjänstlistan
};

// Callback när någon läser eller skriver på karakteristiken
static int gatt_chr_access_cb(uint16_t conn_handle,
                              uint16_t attr_handle,
                              struct ble_gatt_access_ctxt *ctxt,
                              void *arg)
{
    int rc;

    switch (ctxt->op) {
        case BLE_GATT_ACCESS_OP_READ_CHR:   // Om mobilen läser karakteristiken
            rc = os_mbuf_append(ctxt->om, g_hello_value, strlen(g_hello_value));
            return rc == 0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;  // Returnera data eller fel
        default:
            return BLE_ATT_ERR_UNLIKELY;   // Alla andra operationer nekas
    }
}

// Callback för BLE-händelser som connect/disconnect/advertising klart
static int gap_event_cb(struct ble_gap_event *event, void *arg)
{
    switch (event->type) {
        case BLE_GAP_EVENT_CONNECT:
            if (event->connect.status == 0) {
                ESP_LOGI(TAG, "Phone connected");   // Anslutning lyckades
            } else {
                ESP_LOGI(TAG, "Connection failed, restarting advertising");
                start_advertising();   // Försök annonsera igen
            }
            return 0;

        case BLE_GAP_EVENT_DISCONNECT:
            ESP_LOGI(TAG, "Phone disconnected, restarting advertising");
            start_advertising();   // Starta annonsering igen efter disconnect
            return 0;

        case BLE_GAP_EVENT_ADV_COMPLETE:
            ESP_LOGI(TAG, "Advertising complete, restarting advertising");
            start_advertising();   // Starta om annonsering när den avslutas
            return 0;

        default:
            return 0;
    }
}

// Startar BLE advertising så mobilen kan hitta enheten
static void start_advertising(void)
{
    struct ble_hs_adv_fields fields;
    struct ble_gap_adv_params adv_params;
    int rc;

    memset(&fields, 0, sizeof(fields));   // Nollställ advertising-fälten

    fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;  // BLE only + general discoverable
    
    fields.name = (const uint8_t *)ble_svc_gap_device_name();   // Lägg med enhetsnamnet
    fields.name_len = strlen(ble_svc_gap_device_name());
    fields.name_is_complete = 1;

    // Dessa rader kan aktiveras om du vill annonsera service-UUID också
    //fields.uuids128 = (ble_uuid128_t *)&g_service_uuid;
    //fields.num_uuids128 = 1;
    //fields.uuids128_is_complete = 1;

    rc = ble_gap_adv_set_fields(&fields);   // Sätt advertising-data
    if (rc != 0) {
        ESP_LOGE(TAG, "ble_gap_adv_set_fields failed: %d", rc);
        return;
    }

    memset(&adv_params, 0, sizeof(adv_params));   // Nollställ advertising-parametrar
    adv_params.conn_mode = BLE_GAP_CONN_MODE_UND; // Tillåt anslutningar
    adv_params.disc_mode = BLE_GAP_DISC_MODE_GEN; // General discoverable mode

    rc = ble_gap_adv_start(own_addr_type,
                           NULL,
                           BLE_HS_FOREVER,   // Annonsera tills vidare
                           &adv_params,
                           gap_event_cb,
                           NULL);
    if (rc != 0) {
        ESP_LOGE(TAG, "ble_gap_adv_start failed: %d", rc);
        return;
    }

    ESP_LOGI(TAG, "Advertising started. Scan for: %s", DEVICE_NAME);
}

// Körs när BLE-stackens synk är klar och adressen är redo
static void ble_app_on_sync(void)
{
    int rc;

    rc = ble_hs_id_infer_auto(0, &own_addr_type);   // Välj automatisk adress-typ
    if (rc != 0) {
        ESP_LOGE(TAG, "ble_hs_id_infer_auto failed: %d", rc);
        return;
    }

    start_advertising();   // Börja annonsera när BLE är redo
}

// Task som kör NimBLE-hostens loop
static void ble_host_task(void *param)
{
    ESP_LOGI(TAG, "NimBLE host task started");
    nimble_port_run();               // Starta NimBLE-loop
    nimble_port_freertos_deinit();   // Städa upp om loopen avslutas
}

// Huvudstart för programmet
void app_main(void)
{
    int rc;

    rc = nvs_flash_init();   // Initiera flash för lagring som BLE behöver
    if (rc != 0) {
        ESP_LOGE(TAG, "nvs_flash_init failed: %d", rc);
        return;
    }

    nimble_port_init();   // Initiera NimBLE-stacken

    ble_svc_gap_init();   // Initiera GAP-tjänster
    ble_svc_gatt_init();  // Initiera GATT-tjänster

    rc = ble_svc_gap_device_name_set(DEVICE_NAME);   // Sätt BLE-namnet
    if (rc != 0) {
        ESP_LOGE(TAG, "ble_svc_gap_device_name_set failed: %d", rc);
        return;
    }

    rc = ble_gatts_count_cfg(gatt_svcs);   // Räkna resurser för GATT-tabellen
    if (rc != 0) {
        ESP_LOGE(TAG, "ble_gatts_count_cfg failed: %d", rc);
        return;
    }

    rc = ble_gatts_add_svcs(gatt_svcs);   // Lägg till tjänsterna i GATT-servern
    if (rc != 0) {
        ESP_LOGE(TAG, "ble_gatts_add_svcs failed: %d", rc);
        return;
    }

    ble_hs_cfg.sync_cb = ble_app_on_sync;   // Callback när BLE är redo
    nimble_port_freertos_init(ble_host_task);   // Starta NimBLE-tasken
}