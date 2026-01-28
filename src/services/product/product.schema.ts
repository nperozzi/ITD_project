import { user } from "@/database/schema";
import { relations } from "drizzle-orm";
import * as sqlite from "drizzle-orm/sqlite-core";

export interface ProductPriceDetails {
  currency: {
    code: string;
    symbol: {
      prefix?: string;
      suffix?: string;
    };
  };
  price: {
    value: number;
    per: {
      amount?: number;
      suffix: "unit" | "kg" | "g";
    };
    quantity: {
      amount: number;
      suffix: "unit" | "kg" | "g";
    };
  };
  discount?: {
    percentage: number;
    validUntil: Date;
  };
}

export const product = sqlite.sqliteTable("product", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  ownerId: sqlite
    .text("owner_id")
    .notNull()
    .references(() => user.id),
  display_name: sqlite.text("display_name").notNull(),
  priceDetails: sqlite
    .text("price", { mode: "json" })
    .$type<ProductPriceDetails>()
    .notNull(),
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

export const productRelations = relations(product, ({ one }) => ({
  owner: one(user, {
    fields: [product.ownerId],
    references: [user.id],
  }),
}));
