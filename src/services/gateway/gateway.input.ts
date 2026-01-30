import { z } from "zod";

// ============================================================================
// Gateway Serial Validators
// ============================================================================

/**
 * Validator for creating a new gateway serial number (admin only)
 */
export const createGatewaySerialValidator = z.object({
  serialNumber: z.string().uuid("Serial number must be a valid UUID"),
  notes: z.string().max(500).optional(),
});

/**
 * Validator for checking gateway claim status (used by gateway device)
 */
export const checkGatewayClaimValidator = z.object({
  serialNumber: z.string().min(1, "Serial number is required"),
});

// ============================================================================
// Gateway Validators
// ============================================================================

/**
 * Validator for claiming/registering a gateway
 */
export const claimGatewayValidator = z.object({
  serialNumber: z.string().min(1, "Serial number is required"),
  name: z
    .string()
    .min(1, "Name is required")
    .max(100, "Name must be at most 100 characters"),
});

/**
 * Validator for reading a single gateway
 */
export const readGatewayValidator = z.object({
  id: z.string().uuid("Invalid gateway ID"),
});

/**
 * Validator for updating a gateway
 */
export const updateGatewayValidator = z.object({
  id: z.string().uuid("Invalid gateway ID"),
  name: z.string().min(1).max(100).optional(),
});

/**
 * Validator for deleting a gateway
 */
export const deleteGatewayValidator = z.object({
  id: z.string().uuid("Invalid gateway ID"),
});

// ============================================================================
// Gateway API Validators (used by gateway devices)
// ============================================================================

/**
 * Label data reported by gateway
 */
export const gatewayLabelReportSchema = z.object({
  serialNumber: z.string(),
  batteryPercent: z.number().min(0).max(100).optional(),
  rssi: z.number().int().optional(),
  status: z.enum(["online", "offline", "error", "updating"]),
  lastError: z.string().optional(),
  displayWidth: z.number().optional(),
  displayHeight: z.number().optional(),
});

/**
 * Validator for gateway ping/sync request
 */
export const gatewaySyncValidator = z.object({
  /** Labels currently connected to this gateway */
  labels: z.array(gatewayLabelReportSchema),
  /** Gateway firmware version */
  firmwareVersion: z.string().optional(),
  /** Gateway local IP address */
  ipAddress: z.string().optional(),
});

/**
 * Validator for gateway acknowledging label updates
 */
export const gatewayAckValidator = z.object({
  /** Results of label update attempts */
  results: z.array(
    z.object({
      labelSerialNumber: z.string(),
      success: z.boolean(),
      error: z.string().optional(),
    }),
  ),
});

// ============================================================================
// Type Exports
// ============================================================================

export type CreateGatewaySerialInput = z.infer<
  typeof createGatewaySerialValidator
>;
export type CheckGatewayClaimInput = z.infer<typeof checkGatewayClaimValidator>;
export type ClaimGatewayInput = z.infer<typeof claimGatewayValidator>;
export type ReadGatewayInput = z.infer<typeof readGatewayValidator>;
export type UpdateGatewayInput = z.infer<typeof updateGatewayValidator>;
export type DeleteGatewayInput = z.infer<typeof deleteGatewayValidator>;
export type GatewayLabelReport = z.infer<typeof gatewayLabelReportSchema>;
export type GatewaySyncInput = z.infer<typeof gatewaySyncValidator>;
export type GatewayAckInput = z.infer<typeof gatewayAckValidator>;
