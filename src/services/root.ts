import { createCallerFactory, createTRPCRouter } from "@/services/trpc";
import { userRouter } from "./auth/user/user.router";

export const appRouter = createTRPCRouter({
  user: userRouter,
});

export const createCaller = createCallerFactory(appRouter);

export type AppRouter = typeof appRouter;
