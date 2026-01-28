import { user } from "@/services/auth/auth.schema";
import { product } from "@/services/product/product.schema";
import { relations } from "drizzle-orm";
import * as sqlite from "drizzle-orm/sqlite-core";

/**
 * Gateway Serial Numbers - Pre-registered serial numbers for gateway devices.
 * These are created by admin CLI and act like redeemable gift cards.
 * When a user claims a gateway, they redeem the serial number.
 */
export const gatewaySerial = sqlite.sqliteTable("gateway_serial", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  /** The unique serial number printed on the gateway device */
  serialNumber: sqlite.text("serial_number").notNull().unique(),
  /** Whether this serial has been claimed by a user */
  isClaimed: sqlite
    .integer("is_claimed", { mode: "boolean" })
    .notNull()
    .default(false),
  /** The ID of the gateway record created when claimed */
  gatewayId: sqlite.text("gateway_id"),
  /** Admin notes about this serial (e.g., batch number, manufacturing date) */
  notes: sqlite.text("notes"),
  createdAt: sqlite
    .integer("created_at", { mode: "timestamp" })
    .notNull()
    .$defaultFn(() => new Date()),
  claimedAt: sqlite.integer("claimed_at", { mode: "timestamp" }),
});

/**
 * Gateway - A claimed and registered gateway device owned by a user.
 * The gateway orchestrates communication between the web app and label devices.
 */
export const gateway = sqlite.sqliteTable("gateway", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  /** User-defined name for the gateway (e.g., "Store Front", "Warehouse A") */
  name: sqlite.text("name").notNull(),
  /** The serial number used to claim this gateway */
  serialNumber: sqlite.text("serial_number").notNull().unique(),
  /** The user who owns this gateway */
  ownerId: sqlite
    .text("owner_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  /** API key for gateway authentication (generated on claim) */
  apiKey: sqlite.text("api_key").notNull().unique(),
  /** Current online status */
  isOnline: sqlite
    .integer("is_online", { mode: "boolean" })
    .notNull()
    .default(false),
  /** Last time the gateway pinged the server */
  lastPingAt: sqlite.integer("last_ping_at", { mode: "timestamp" }),
  /** Firmware version reported by the gateway */
  firmwareVersion: sqlite.text("firmware_version"),
  /** IP address of the gateway (for debugging) */
  ipAddress: sqlite.text("ip_address"),
  createdAt: sqlite
    .integer("created_at", { mode: "timestamp" })
    .notNull()
    .$defaultFn(() => new Date()),
  updatedAt: sqlite
    .integer("updated_at", { mode: "timestamp" })
    .notNull()
    .$defaultFn(() => new Date())
    .$onUpdateFn(() => new Date()),
});

export const gatewaySerialRelations = relations(gatewaySerial, ({ one }) => ({
  gateway: one(gateway, {
    fields: [gatewaySerial.gatewayId],
    references: [gateway.id],
  }),
}));

export const gatewayRelations = relations(gateway, ({ one, many }) => ({
  owner: one(user, {
    fields: [gateway.ownerId],
    references: [user.id],
  }),
  labels: many(label),
}));

// ============================================================================
// Label Tables and Relations
// ============================================================================

/**
 * Label Serial Numbers - Pre-registered serial numbers for ESL label devices.
 * These are created by admin CLI, similar to gateway serials.
 */
export const labelSerial = sqlite.sqliteTable("label_serial", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  /** The unique serial number printed on the label device */
  serialNumber: sqlite.text("serial_number").notNull().unique(),
  /** Whether this serial has been claimed by a user */
  isClaimed: sqlite
    .integer("is_claimed", { mode: "boolean" })
    .notNull()
    .default(false),
  /** The ID of the label record created when claimed */
  labelId: sqlite.text("label_id"),
  /** Admin notes about this serial */
  notes: sqlite.text("notes"),
  createdAt: sqlite
    .integer("created_at", { mode: "timestamp" })
    .notNull()
    .$defaultFn(() => new Date()),
  claimedAt: sqlite.integer("claimed_at", { mode: "timestamp" }),
});

/**
 * Label Status Enum - Possible states of a label device
 */
export type LabelStatus =
  | "pending" // User requested to add, waiting for gateway to find it
  | "online" // Label is connected and working
  | "offline" // Label was connected but lost connection
  | "error" // An error occurred (see lastError field)
  | "updating"; // Currently updating display

/**
 * Label - An electronic shelf label device registered by a user.
 * Labels are discovered by gateways and can display product information.
 */
export const label = sqlite.sqliteTable("label", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  /** User-defined name for the label (e.g., "Aisle 1 - Shelf 3") */
  name: sqlite.text("name").notNull(),
  /** The serial number of this label device */
  serialNumber: sqlite.text("serial_number").notNull().unique(),
  /** The user who owns this label */
  ownerId: sqlite
    .text("owner_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  /** The gateway currently connected to this label (null if not connected) */
  gatewayId: sqlite.text("gateway_id").references(() => gateway.id, {
    onDelete: "set null",
  }),
  /** The product currently assigned to this label (null if blank) */
  productId: sqlite.text("product_id"),
  /** Current status of the label */
  status: sqlite
    .text("status", {
      enum: ["pending", "online", "offline", "error", "updating"],
    })
    .notNull()
    .default("pending"),
  /** Battery percentage (0-100), null if unknown */
  batteryPercent: sqlite.integer("battery_percent"),
  /** Last error message if status is 'error' */
  lastError: sqlite.text("last_error"),
  /** Last time the label was updated successfully */
  lastUpdateAt: sqlite.integer("last_update_at", { mode: "timestamp" }),
  /** Last time we received data from this label via gateway */
  lastSeenAt: sqlite.integer("last_seen_at", { mode: "timestamp" }),
  /** Display width in pixels */
  displayWidth: sqlite.integer("display_width"),
  /** Display height in pixels */
  displayHeight: sqlite.integer("display_height"),
  createdAt: sqlite
    .integer("created_at", { mode: "timestamp" })
    .notNull()
    .$defaultFn(() => new Date()),
  updatedAt: sqlite
    .integer("updated_at", { mode: "timestamp" })
    .notNull()
    .$defaultFn(() => new Date())
    .$onUpdateFn(() => new Date()),
});

export const labelSerialRelations = relations(labelSerial, ({ one }) => ({
  label: one(label, {
    fields: [labelSerial.labelId],
    references: [label.id],
  }),
}));

export const labelRelations = relations(label, ({ one }) => ({
  owner: one(user, {
    fields: [label.ownerId],
    references: [user.id],
  }),
  gateway: one(gateway, {
    fields: [label.gatewayId],
    references: [gateway.id],
  }),
  product: one(product, {
    fields: [label.productId],
    references: [product.id],
  }),
}));
