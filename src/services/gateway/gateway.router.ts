import "server-cli-only";

import {
  claimGatewayValidator,
  deleteGatewayValidator,
  readGatewayValidator,
  updateGatewayValidator,
} from "@/services/gateway/gateway.input";
import { gatewayService } from "@/services/gateway/gateway.service";
import {
  assignProductToLabelValidator,
  deleteLabelValidator,
  readLabelValidator,
  registerLabelValidator,
  updateLabelValidator,
} from "@/services/gateway/label/label.input";
import { createTRPCRouter, protectedProcedure } from "@/services/trpc";

/**
 * Gateway Router - tRPC procedures for gateway management.
 * Used by authenticated users to manage their gateways and labels.
 */
export const gatewayRouter = createTRPCRouter({
  // ============================================================================
  // Gateway Operations
  // ============================================================================

  /**
   * Claim a gateway using a serial number.
   * This "redeems" the serial and creates a gateway record for the user.
   */
  claim: protectedProcedure
    .input(claimGatewayValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.claim({
        serialNumber: input.serialNumber,
        name: input.name,
        ownerId: ctx.user.id,
      });
    }),

  /**
   * Get a specific gateway by ID.
   */
  read: protectedProcedure
    .input(readGatewayValidator)
    .query(async ({ input, ctx }) => {
      return await gatewayService.read({
        id: input.id,
        ownerId: ctx.user.id,
      });
    }),

  /**
   * Get all gateways for the current user.
   */
  readAll: protectedProcedure.query(async ({ ctx }) => {
    return await gatewayService.readAll({
      ownerId: ctx.user.id,
    });
  }),

  /**
   * Update a gateway's settings.
   */
  update: protectedProcedure
    .input(updateGatewayValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.update({
        id: input.id,
        ownerId: ctx.user.id,
        name: input.name,
      });
    }),

  /**
   * Delete a gateway.
   */
  delete: protectedProcedure
    .input(deleteGatewayValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.delete({
        id: input.id,
        ownerId: ctx.user.id,
      });
    }),

  // ============================================================================
  // Label Operations (nested under gateway for organization)
  // ============================================================================

  /**
   * Register a label device.
   * Creates a label in 'pending' status, waiting for a gateway to find it.
   */
  registerLabel: protectedProcedure
    .input(registerLabelValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.label.register({
        serialNumber: input.serialNumber,
        name: input.name,
        ownerId: ctx.user.id,
      });
    }),

  /**
   * Get a specific label by ID.
   */
  readLabel: protectedProcedure
    .input(readLabelValidator)
    .query(async ({ input, ctx }) => {
      return await gatewayService.label.read({
        id: input.id,
        ownerId: ctx.user.id,
      });
    }),

  /**
   * Get all labels for the current user.
   */
  readAllLabels: protectedProcedure.query(async ({ ctx }) => {
    return await gatewayService.label.readAll({
      ownerId: ctx.user.id,
    });
  }),

  /**
   * Update a label's settings.
   */
  updateLabel: protectedProcedure
    .input(updateLabelValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.label.update({
        id: input.id,
        ownerId: ctx.user.id,
        name: input.name,
        productId: input.productId,
      });
    }),

  /**
   * Assign a product to a label.
   */
  assignProductToLabel: protectedProcedure
    .input(assignProductToLabelValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.label.assignProduct({
        labelId: input.labelId,
        productId: input.productId,
        ownerId: ctx.user.id,
      });
    }),

  /**
   * Delete a label.
   */
  deleteLabel: protectedProcedure
    .input(deleteLabelValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.label.delete({
        id: input.id,
        ownerId: ctx.user.id,
      });
    }),
});
