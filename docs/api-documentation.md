# ESL Gateway API Documentation

This document describes the REST API endpoints for Electronic Shelf Label (ESL) gateway devices. These endpoints are used by gateway hardware to communicate with the server.

## Overview

The system follows a "claim" model similar to redeemable gift cards:

1. **Admin creates serial numbers** - Using the admin CLI, serial numbers are pre-registered in the system
2. **User claims gateway** - Through the web app, users enter a serial number to claim a gateway
3. **Gateway checks claim status** - The gateway periodically polls to check if it has been claimed
4. **Gateway syncs data** - Once claimed, the gateway syncs label information and receives updates

## Base URL

```
https://your-domain.com/api/gateway
```

## Authentication

Gateways authenticate using an API key provided after claim. Include the key in the `Authorization` header:

```
Authorization: Bearer <api_key>
```

---

## Endpoints

### 1. Check Claim Status

Check if a gateway serial number has been claimed by a user.

**Endpoint:** `GET /api/gateway/claim`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `serial` | string | Yes | The gateway serial number |

**Response (Unclaimed):**

```json
{
  "status": "unclaimed",
  "message": "Gateway not yet claimed. Please claim via web app."
}
```

**Response (Claimed):**

```json
{
  "status": "claimed",
  "apiKey": "gw_abc123...",
  "gatewayId": "clxyz789...",
  "ownerId": "user_456...",
  "name": "Store Gateway 1"
}
```

**Response (Invalid Serial):**

```json
{
  "status": "invalid",
  "message": "Serial number not found"
}
```

**Status Codes:**

- `200 OK` - Request successful (check `status` field for result)
- `400 Bad Request` - Missing serial parameter

**Example:**

```bash
curl "https://your-domain.com/api/gateway/claim?serial=550e8400-e29b-41d4-a716-446655440000"
```

---

### 2. Sync Gateway Data

Send label discovery data to the server and receive updates to push to labels.

**Endpoint:** `POST /api/gateway/sync`

**Headers:**

```
Authorization: Bearer <api_key>
Content-Type: application/json
```

**Request Body:**

```json
{
  "firmwareVersion": "1.2.0",
  "labels": [
    {
      "serialNumber": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "batteryPercent": 85,
      "rssi": -45,
      "firmwareVersion": "2.1.0"
    },
    {
      "serialNumber": "3f333df6-90a4-4fda-8dd3-9485d27cee36",
      "batteryPercent": 72,
      "rssi": -52,
      "firmwareVersion": "2.1.0"
    }
  ]
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `firmwareVersion` | string | No | Gateway firmware version |
| `labels` | array | Yes | Array of discovered label devices |
| `labels[].serialNumber` | string | Yes | Label serial number |
| `labels[].batteryPercent` | number | No | Battery level (0-100) |
| `labels[].rssi` | number | No | Signal strength in dBm |
| `labels[].firmwareVersion` | string | No | Label firmware version |

**Response (Success):**

```json
{
  "success": true,
  "gateway": {
    "id": "gateway_123",
    "name": "Store Gateway 1"
  },
  "labels": {
    "connected": 2,
    "pending": 1,
    "updated": 0
  },
  "updates": [
    {
      "labelId": "label_abc",
      "serialNumber": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "productId": "prod_xyz",
      "product": {
        "id": "prod_xyz",
        "name": "Chicken Breast",
        "brand": "Fresh Farm",
        "barcode": "7350123456789",
        "sku": "CHK-BRST-001",
        "priceDetails": {
          "currency": {
            "code": "SEK",
            "symbol": { "suffix": " kr" },
            "decimalPlaces": 2
          },
          "priceInCents": 8990,
          "priceUnit": "kg",
          "quantity": 1,
          "quantityUnit": "kg",
          "discount": {
            "percentage": 20,
            "validUntil": "2025-01-31"
          }
        }
      }
    }
  ]
}
```

**Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the sync was successful |
| `gateway` | object | Gateway information |
| `labels.connected` | number | Number of labels now connected to this gateway |
| `labels.pending` | number | Number of labels waiting for updates |
| `labels.updated` | number | Number of labels that received updates this sync |
| `updates` | array | Labels that need display updates |
| `updates[].labelId` | string | Internal label ID |
| `updates[].serialNumber` | string | Label serial number |
| `updates[].productId` | string | Assigned product ID |
| `updates[].product` | object | Full product data for display |

**Status Codes:**

- `200 OK` - Sync successful
- `401 Unauthorized` - Invalid or missing API key
- `400 Bad Request` - Invalid request body

**Example:**

```bash
curl -X POST "https://your-domain.com/api/gateway/sync" \
  -H "Authorization: Bearer gw_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "firmwareVersion": "1.2.0",
    "labels": [
      {"serialNumber": "7c9e6679-7425-40de-944b-e07fc1f90ae7", "batteryPercent": 85}
    ]
  }'
```

---

### 3. Acknowledge Updates

Confirm that updates have been successfully pushed to labels.

**Endpoint:** `PUT /api/gateway/sync`

**Headers:**

```
Authorization: Bearer <api_key>
Content-Type: application/json
```

**Request Body:**

```json
{
  "results": [
    {
      "labelId": "label_abc",
      "success": true
    },
    {
      "labelId": "label_def",
      "success": false,
      "error": "Communication timeout"
    }
  ]
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `results` | array | Yes | Array of update results |
| `results[].labelId` | string | Yes | The label ID from the sync response |
| `results[].success` | boolean | Yes | Whether the update was successful |
| `results[].error` | string | No | Error message if update failed |

**Response:**

```json
{
  "success": true,
  "processed": 2,
  "successful": 1,
  "failed": 1
}
```

**Status Codes:**

- `200 OK` - Acknowledgment processed
- `401 Unauthorized` - Invalid or missing API key
- `400 Bad Request` - Invalid request body

**Example:**

```bash
curl -X PUT "https://your-domain.com/api/gateway/sync" \
  -H "Authorization: Bearer gw_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "results": [
      {"labelId": "label_abc", "success": true}
    ]
  }'
```

---

## Gateway Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Gateway   │     │   Server    │     │   Web App   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  GET /claim?serial│                   │
       │──────────────────>│                   │
       │  status: unclaimed│                   │
       │<──────────────────│                   │
       │                   │                   │
       │         ... user claims gateway ...   │
       │                   │                   │
       │                   │   POST claim      │
       │                   │<──────────────────│
       │                   │   success         │
       │                   │──────────────────>│
       │                   │                   │
       │  GET /claim?serial│                   │
       │──────────────────>│                   │
       │  status: claimed  │                   │
       │  apiKey: gw_xxx   │                   │
       │<──────────────────│                   │
       │                   │                   │
       │  POST /sync       │                   │
       │  (with labels)    │                   │
       │──────────────────>│                   │
       │  updates: [...]   │                   │
       │<──────────────────│                   │
       │                   │                   │
       │  PUT /sync        │                   │
       │  (ack results)    │                   │
       │──────────────────>│                   │
       │  success          │                   │
       │<──────────────────│                   │
       │                   │                   │
```

---

## Product Price Details Schema

The `priceDetails` object contains all pricing information for a product:

```typescript
interface ProductPriceDetails {
  currency: {
    code: string; // ISO 4217 code (e.g., "SEK", "USD", "EUR")
    symbol: {
      prefix?: string; // e.g., "$", "€"
      suffix?: string; // e.g., " kr"
    };
    decimalPlaces: number; // Usually 2
  };
  priceInCents: number; // Price in smallest currency unit
  priceUnit: string; // "unit", "kg", "l", "m", etc.
  quantity: number; // Package quantity
  quantityUnit: string; // Unit for quantity
  discount?: {
    percentage: number; // Discount percentage (e.g., 20 for 20%)
    validUntil: string; // ISO 8601 date (YYYY-MM-DD)
  };
}
```

### Displaying Prices

To display the price correctly:

```javascript
function formatPrice(priceDetails) {
  const value =
    priceDetails.priceInCents /
    Math.pow(10, priceDetails.currency.decimalPlaces);

  const formatted = value.toFixed(priceDetails.currency.decimalPlaces);
  const prefix = priceDetails.currency.symbol.prefix || "";
  const suffix = priceDetails.currency.symbol.suffix || "";

  return `${prefix}${formatted}${suffix}`;
}

// Example: priceInCents=8990, SEK → "89.90 kr"
// Example: priceInCents=1999, USD → "$19.99"
```

### Calculating Discounted Price

```javascript
function getDiscountedPrice(priceDetails) {
  if (!priceDetails.discount) return priceDetails.priceInCents;

  const discountMultiplier = 1 - priceDetails.discount.percentage / 100;
  return Math.round(priceDetails.priceInCents * discountMultiplier);
}

// Example: 8990 with 20% discount → 7192 (71.92 kr)
```

---

## Label Status Values

| Status     | Description                                        |
| ---------- | -------------------------------------------------- |
| `pending`  | Label registered but not yet discovered by gateway |
| `online`   | Label connected and synced with gateway            |
| `offline`  | Label was connected but not seen in recent sync    |
| `updating` | Label is receiving a display update                |
| `error`    | Label encountered an error                         |

---

## Error Handling

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

Common error codes:

- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limits are enforced. Recommended polling intervals:

- **Claim status check:** Every 30 seconds while unclaimed
- **Sync:** Every 60 seconds while online
- **Acknowledgment:** Immediately after processing updates

---

## Admin CLI

For managing serial numbers, use the admin CLI. Serial numbers are auto-generated UUIDs:

```bash
# Create a single gateway serial
bun run scripts/admin.ts gateway:create

# Create 10 gateway serials
bun run scripts/admin.ts gateway:create 10

# Create with notes
bun run scripts/admin.ts gateway:create 5 --notes="Manufacturing Batch A"

# List all gateway serials
bun run scripts/admin.ts gateway:list

# Create label serials
bun run scripts/admin.ts label:create

# Batch create label serials
bun run scripts/admin.ts label:create 50 --notes="2.9 inch displays"

# List all label serials
bun run scripts/admin.ts label:list
```
