import { z } from "zod";

// ============================================================================
// Label Serial Validators
// ============================================================================

/**
 * Validator for creating a new label serial number (admin only)
 */
export const createLabelSerialValidator = z.object({
  serialNumber: z.string().uuid("Serial number must be a valid UUID"),
  notes: z.string().max(500).optional(),
});

// ============================================================================
// Label Validators
// ============================================================================

/**
 * Validator for registering a label (user initiates, gateway finds it)
 */
export const registerLabelValidator = z.object({
  serialNumber: z.string().min(1, "Serial number is required"),
  name: z
    .string()
    .min(1, "Name is required")
    .max(100, "Name must be at most 100 characters"),
});

/**
 * Validator for reading a single label
 */
export const readLabelValidator = z.object({
  id: z.string().uuid("Invalid label ID"),
});

/**
 * Validator for updating a label
 */
export const updateLabelValidator = z.object({
  id: z.string().uuid("Invalid label ID"),
  name: z.string().min(1).max(100).optional(),
  productId: z.string().uuid("Invalid product ID").nullable().optional(),
});

/**
 * Validator for deleting a label
 */
export const deleteLabelValidator = z.object({
  id: z.string().uuid("Invalid label ID"),
});

/**
 * Validator for assigning a product to a label
 */
export const assignProductToLabelValidator = z.object({
  labelId: z.string().uuid("Invalid label ID"),
  productId: z.string().uuid("Invalid product ID").nullable(),
});

// ============================================================================
// Type Exports
// ============================================================================

export type CreateLabelSerialInput = z.infer<typeof createLabelSerialValidator>;
export type RegisterLabelInput = z.infer<typeof registerLabelValidator>;
export type ReadLabelInput = z.infer<typeof readLabelValidator>;
export type UpdateLabelInput = z.infer<typeof updateLabelValidator>;
export type DeleteLabelInput = z.infer<typeof deleteLabelValidator>;
export type AssignProductToLabelInput = z.infer<
  typeof assignProductToLabelValidator
>;
