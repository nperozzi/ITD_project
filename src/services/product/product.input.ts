import z from "zod";

export const createProductValidator = z.object({
  name: z.string().min(1).max(255),
  type: z.enum(["gateway", "product"]),
});

export const readProductValidator = z.object({
  id: z.uuid(),
});

export const updateProductValidator = z.object({
  id: z.uuid(),
  data: z.object({
    name: z.string().min(1).max(255).optional(),
    type: z.enum(["gateway", "product"]).optional(),
  }),
});

export const deleteProductValidator = z.object({
  id: z.uuid(),
});
