import "server-cli-only";

import { deviceService } from "@/services/device/device.service";
import {
  createGatewayValidator,
  readGatewayValidator,
  updateGatewayValidator,
} from "@/services/gateway/gateway.input";
import { gatewayService } from "@/services/gateway/gateway.service";
import { createTRPCRouter, protectedProcedure } from "@/services/trpc";

export const gatewayRouter = createTRPCRouter({
  create: protectedProcedure
    .input(createGatewayValidator)
    .mutation(async ({ input, ctx }) => {
      // Create device first
      const device = await deviceService.create({
        ownerId: ctx.user.id,
        name: input.name,
        type: input.type,
      });

      // Then create gateway with the device ID
      if (device) {
        return await gatewayService.create({
          name: input.name,
          deviceId: device.id,
        });
      }
    }),
  read: protectedProcedure
    .input(readGatewayValidator)
    .query(async ({ input, ctx }) => {
      return await gatewayService.read({
        ...input,
      });
    }),
  readAll: protectedProcedure.query(async ({ ctx }) => {
    return await gatewayService.readAll({});
  }),
  update: protectedProcedure
    .input(updateGatewayValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.update({
        ...input,
      });
    }),
  delete: protectedProcedure
    .input(readGatewayValidator)
    .mutation(async ({ input, ctx }) => {
      return await gatewayService.delete({
        ...input,
      });
    }),
});
