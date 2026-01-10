import { createTRPCRouter } from "@/services/trpc";

export const appRouter = createTRPCRouter({});

export type AppRouter = typeof appRouter;
