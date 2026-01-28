import { user } from "@/database/schema";
import { relations } from "drizzle-orm";
import * as sqlite from "drizzle-orm/sqlite-core";

export const device = sqlite.sqliteTable("device", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  ownerId: sqlite
    .text("owner_id")
    .notNull()
    .references(() => user.id),
  name: sqlite.text("name").notNull(),
  type: sqlite.text("type", { enum: ["gateway", "label"] }).notNull(),
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

export const deviceRelations = relations(device, ({ one }) => ({
  owner: one(user, {
    fields: [device.ownerId],
    references: [user.id],
  }),
}));
