import "server-cli-only";

import {
  createProductValidator,
  deleteProductValidator,
  readProductValidator,
  updateProductValidator,
} from "@/services/product/product.input";
import { productService } from "@/services/product/product.service";
import { createTRPCRouter, protectedProcedure } from "@/services/trpc";

/**
 * Product Router - tRPC procedures for product management.
 * Used by authenticated users to manage their product catalog.
 */
export const productRouter = createTRPCRouter({
  /**
   * Create a new product.
   */
  create: protectedProcedure
    .input(createProductValidator)
    .mutation(async ({ input, ctx }) => {
      return await productService.create({
        ownerId: ctx.user.id,
        name: input.name,
        brand: input.brand,
        barcode: input.barcode,
        sku: input.sku,
        description: input.description,
        priceDetails: input.priceDetails,
      });
    }),

  /**
   * Get a specific product by ID.
   */
  read: protectedProcedure
    .input(readProductValidator)
    .query(async ({ input, ctx }) => {
      return await productService.read({
        id: input.id,
        ownerId: ctx.user.id,
      });
    }),

  /**
   * Get all products for the current user.
   */
  readAll: protectedProcedure.query(async ({ ctx }) => {
    return await productService.readAll({
      ownerId: ctx.user.id,
    });
  }),

  /**
   * Get all active products for the current user.
   */
  readActive: protectedProcedure.query(async ({ ctx }) => {
    return await productService.readActive({
      ownerId: ctx.user.id,
    });
  }),

  /**
   * Update a product.
   */
  update: protectedProcedure
    .input(updateProductValidator)
    .mutation(async ({ input, ctx }) => {
      return await productService.update({
        id: input.id,
        ownerId: ctx.user.id,
        name: input.name,
        brand: input.brand,
        barcode: input.barcode,
        sku: input.sku,
        description: input.description,
        priceDetails: input.priceDetails,
        isActive: input.isActive,
      });
    }),

  /**
   * Delete a product.
   */
  delete: protectedProcedure
    .input(deleteProductValidator)
    .mutation(async ({ input, ctx }) => {
      return await productService.delete({
        id: input.id,
        ownerId: ctx.user.id,
      });
    }),
});
