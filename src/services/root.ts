import { gatewayRouter } from "@/services/gateway/gateway.router";
import { productRouter } from "@/services/product/product.router";
import { createCallerFactory, createTRPCRouter } from "@/services/trpc";

export const appRouter = createTRPCRouter({
  gateway: gatewayRouter,
  product: productRouter,
});

export const createCaller = createCallerFactory(appRouter);

export type AppRouter = typeof appRouter;
