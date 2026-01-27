import { z } from "zod";

export const getUserByIdValidator = z.object({
  userId: z.string(),
});

export const getUserByUsernameValidator = z.object({
  username: z.string(),
});

export const getUserByEmailValidator = z.object({
  email: z.string().email(),
});

export const updateUserValidator = z.object({
  name: z.string().optional(),
  username: z.string().optional(),
  image: z.string().optional(),
});

export const createUserValidator = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
  username: z.string().optional(),
  image: z.string().optional(),
});

export const deleteUserValidator = z.object({
  userId: z.string(),
});
