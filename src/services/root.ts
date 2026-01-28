import { deviceRouter } from "@/services/device/device.router";
import { gatewayRouter } from "@/services/gateway/gateway.router";
import { createCallerFactory, createTRPCRouter } from "@/services/trpc";

export const appRouter = createTRPCRouter({
  device: deviceRouter,
  gateway: gatewayRouter,
});

export const createCaller = createCallerFactory(appRouter);

export type AppRouter = typeof appRouter;
