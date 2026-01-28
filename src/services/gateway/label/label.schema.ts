import { device, product, user } from "@/database/schema";
import { relations } from "drizzle-orm";
import * as sqlite from "drizzle-orm/sqlite-core";

export const label = sqlite.sqliteTable("label", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  name: sqlite.text("name").notNull(),
  batteryPercentage: sqlite.real("battery_percentage"),
  productId: sqlite
    .text("product_id")
    .notNull()
    .references(() => product.id),
  ownerId: sqlite
    .text("owner_id")
    .notNull()
    .references(() => user.id),
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

export const labelRelations = relations(label, ({ one }) => ({
  device: one(device, {
    fields: [label.deviceId],
    references: [device.id],
  }),
  product: one(product, {
    fields: [label.productId],
    references: [product.id],
  }),
  owner: one(user, {
    fields: [label.ownerId],
    references: [user.id],
  }),
}));
