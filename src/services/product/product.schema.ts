import { label, user } from "@/database/schema";
import { relations } from "drizzle-orm";
import * as sqlite from "drizzle-orm/sqlite-core";

/**
 * Currency configuration for price display
 */
export interface ProductCurrency {
  /** ISO 4217 currency code (e.g., "SEK", "USD", "EUR") */
  code: string;
  /** Symbol configuration */
  symbol: {
    /** Symbol displayed before the price (e.g., "$") */
    prefix?: string;
    /** Symbol displayed after the price (e.g., " kr") */
    suffix?: string;
  };
  /** Number of decimal places for this currency */
  decimalPlaces: number;
}

/**
 * Unit types for product quantities
 */
export type ProductUnit =
  | "unit"
  | "kg"
  | "g"
  | "l"
  | "ml"
  | "m"
  | "cm"
  | "piece";

/**
 * Discount configuration
 */
export interface ProductDiscount {
  /** Discount percentage (e.g., 10 for 10% off) */
  percentage: number;
  /** When the discount expires */
  validUntil: string; // ISO date string
}

/**
 * Complete price details for a product
 */
export interface ProductPriceDetails {
  /** Currency configuration */
  currency: ProductCurrency;
  /** Price in smallest currency unit (e.g., cents, öre) */
  priceInCents: number;
  /** What unit the price is for */
  priceUnit: ProductUnit;
  /** Quantity amount (e.g., 500 for "500g") */
  quantity: number;
  /** Quantity unit */
  quantityUnit: ProductUnit;
  /** Optional discount */
  discount?: ProductDiscount;
}

/**
 * Product - A product that can be assigned to labels for display.
 */
export const product = sqlite.sqliteTable("product", {
  id: sqlite
    .text("id")
    .primaryKey()
    .$defaultFn(() => crypto.randomUUID()),
  /** The user who owns this product */
  ownerId: sqlite
    .text("owner_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  /** Display name shown on label (e.g., "Chicken Breast") */
  name: sqlite.text("name").notNull(),
  /** Brand name (e.g., "Fresh Farm") */
  brand: sqlite.text("brand"),
  /** Product barcode (EAN/UPC) */
  barcode: sqlite.text("barcode"),
  /** SKU or internal product code */
  sku: sqlite.text("sku"),
  /** Product description */
  description: sqlite.text("description"),
  /** Price details as JSON */
  priceDetails: sqlite
    .text("price_details", { mode: "json" })
    .$type<ProductPriceDetails>()
    .notNull(),
  /** Whether this product is currently active */
  isActive: sqlite
    .integer("is_active", { mode: "boolean" })
    .notNull()
    .default(true),
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

export const productRelations = relations(product, ({ one, many }) => ({
  owner: one(user, {
    fields: [product.ownerId],
    references: [user.id],
  }),
  labels: many(label),
}));
