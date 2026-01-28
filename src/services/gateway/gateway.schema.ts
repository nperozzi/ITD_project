import { label } from "@/database/schema";
import { device } from "@/services/device/device.schema";
import { relations } from "drizzle-orm";
import * as sqlite from "drizzle-orm/sqlite-core";

export * from "./label/label.schema";

export const gateway = sqlite.sqliteTable("gateway", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  name: sqlite.text("name").notNull(),
  deviceId: sqlite
    .text("device_id")
    .notNull()
    .unique()
    .references(() => device.id),
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

export const gatewayRelations = relations(gateway, ({ one, many }) => ({
  device: one(device, {
    fields: [gateway.deviceId],
    references: [device.id],
  }),
  labels: many(label),
}));
