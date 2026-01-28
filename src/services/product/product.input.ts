import { z } from "zod";

// ============================================================================
// Currency Configuration Schema
// ============================================================================

export const currencySchema = z.object({
  code: z.string().length(3, "Currency code must be 3 characters (ISO 4217)"),
  symbol: z.object({
    prefix: z.string().optional(),
    suffix: z.string().optional(),
  }),
  decimalPlaces: z.number().min(0).max(4).default(2),
});

// ============================================================================
// Product Unit Schema
// ============================================================================

export const productUnitSchema = z.enum([
  "unit",
  "kg",
  "g",
  "l",
  "ml",
  "m",
  "cm",
  "piece",
]);

// ============================================================================
// Discount Schema
// ============================================================================

export const discountSchema = z.object({
  percentage: z.number().min(0).max(100),
  validUntil: z.string(), // ISO date string
});

// ============================================================================
// Price Details Schema
// ============================================================================

export const priceDetailsSchema = z.object({
  currency: currencySchema,
  priceInCents: z.number().int().min(0),
  priceUnit: productUnitSchema,
  quantity: z.number().min(0),
  quantityUnit: productUnitSchema,
  discount: discountSchema.optional(),
});

// ============================================================================
// Product Validators
// ============================================================================

/**
 * Validator for creating a new product
 */
export const createProductValidator = z.object({
  name: z
    .string()
    .min(1, "Name is required")
    .max(100, "Name must be at most 100 characters"),
  brand: z.string().max(100).optional(),
  barcode: z.string().max(50).optional(),
  sku: z.string().max(50).optional(),
  description: z.string().max(500).optional(),
  priceDetails: priceDetailsSchema,
});

/**
 * Validator for reading a single product
 */
export const readProductValidator = z.object({
  id: z.string().uuid("Invalid product ID"),
});

/**
 * Validator for updating a product
 */
export const updateProductValidator = z.object({
  id: z.string().uuid("Invalid product ID"),
  name: z.string().min(1).max(100).optional(),
  brand: z.string().max(100).nullable().optional(),
  barcode: z.string().max(50).nullable().optional(),
  sku: z.string().max(50).nullable().optional(),
  description: z.string().max(500).nullable().optional(),
  priceDetails: priceDetailsSchema.optional(),
  isActive: z.boolean().optional(),
});

/**
 * Validator for deleting a product
 */
export const deleteProductValidator = z.object({
  id: z.string().uuid("Invalid product ID"),
});

// ============================================================================
// Type Exports
// ============================================================================

export type CreateProductInput = z.infer<typeof createProductValidator>;
export type ReadProductInput = z.infer<typeof readProductValidator>;
export type UpdateProductInput = z.infer<typeof updateProductValidator>;
export type DeleteProductInput = z.infer<typeof deleteProductValidator>;
export type PriceDetailsInput = z.infer<typeof priceDetailsSchema>;
