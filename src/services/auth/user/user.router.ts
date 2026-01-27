import "server-only";

import {
  createTRPCRouter,
  protectedProcedure,
  publicProcedure,
} from "@/services/trpc";
import {
  createUserValidator,
  deleteUserValidator,
  getUserByEmailValidator,
  getUserByIdValidator,
  getUserByUsernameValidator,
  updateUserValidator,
} from "./user.input";
import { userService } from "./user.service";

export const userRouter = createTRPCRouter({
  getById: publicProcedure
    .input(getUserByIdValidator)
    .query(async ({ input }) => {
      const result = await userService.read({
        userId: input.userId,
      });

      return result;
    }),

  getByUsername: publicProcedure
    .input(getUserByUsernameValidator)
    .query(async ({ input }) => {
      const result = await userService.readByUsername({
        username: input.username,
      });

      return result;
    }),

  getByEmail: publicProcedure
    .input(getUserByEmailValidator)
    .query(async ({ input }) => {
      const result = await userService.readByEmail({
        email: input.email,
      });

      return result;
    }),

  create: protectedProcedure
    .input(createUserValidator)
    .mutation(async ({ input }) => {
      const result = await userService.create(input);

      return result;
    }),

  update: protectedProcedure
    .input(updateUserValidator)
    .mutation(async ({ ctx, input }) => {
      const result = await userService.update({
        userId: ctx.user.id,
        data: input,
      });

      return result;
    }),

  delete: protectedProcedure
    .input(deleteUserValidator)
    .mutation(async ({ input }) => {
      const result = await userService.delete({
        userId: input.userId,
      });

      return result;
    }),
});
