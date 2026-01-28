import "server-cli-only";

import { deviceService } from "@/services/device/device.service";
import {
  createProductValidator,
  readProductValidator,
  updateProductValidator,
} from "@/services/product/product.input";
import { productService } from "@/services/product/product.service";
import { createTRPCRouter, protectedProcedure } from "@/services/trpc";

export const productRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createProductValidator)
    .mutation(async ({ input, ctx }) => {
      // Create device first
      const device = await deviceService.create({
        ownerId: ctx.user.id,
        name: input.name,
        type: input.type,
      });

      // Then create product with the device ID
      if (device) {
        return await productService.create({
          name: input.name,
          deviceId: device.id,
        });
      }
    }),
  read: protectedProcedure
    .input(readProductValidator)
    .query(async ({ input, ctx }) => {
      return await productService.read({
        ...input,
      });
    }),
  readAll: protectedProcedure.query(async ({ ctx }) => {
    return await productService.readAll({});
  }),
  update: protectedProcedure
    .input(updateProductValidator)
    .mutation(async ({ input, ctx }) => {
      return await productService.update({
        ...input,
      });
    }),
  delete: protectedProcedure
    .input(readProductValidator)
    .mutation(async ({ input, ctx }) => {
      return await productService.delete({
        ...input,
      });
    }),
});
