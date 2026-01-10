import { initTRPC, TRPCError } from "@trpc/server";
import superjson from "superjson";
import { ZodError } from "zod";

import { db } from "@/database";
import { auth } from "@/lib/better-auth";
import Logger from "@/lib/logger";

export const createTRPCContext = async (opts: { headers: Headers }) => {
  const session = await auth.api.getSession({ headers: opts.headers });

  let authObjects = {
    session: session?.session ?? null,
    user: session?.user ?? null,
  };

  return {
    db,
    ...authObjects,
    ...opts,
  };
};

export type TRPCContext = Awaited<ReturnType<typeof createTRPCContext>>;

const t = initTRPC.context<typeof createTRPCContext>().create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

export const createCallerFactory = t.createCallerFactory;

export const createTRPCRouter = t.router;

// TODO: Centralized logging service for issue tracking
const loggingMiddleware = t.middleware(async ({ next, path }) => {
  const logger = new Logger("TRPCMiddleware");

  logger.debug('Path "' + path + '" was accessed.');

  return await next();
});

export const publicProcedure = t.procedure.use(loggingMiddleware);

export const protectedProcedure = t.procedure
  .use(loggingMiddleware)
  .use(({ ctx, next }) => {
    if (!ctx.session || !ctx.user) {
      throw new TRPCError({ code: "UNAUTHORIZED" });
    }

    return next({
      ctx: {
        session: ctx.session,
        user: ctx.user,
      },
    });
  });
