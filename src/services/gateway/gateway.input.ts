import z from "zod";

export const createGatewayValidator = z.object({
  name: z.string().min(1).max(255),
  type: z.enum(["gateway", "label"]),
});

export const readGatewayValidator = z.object({
  id: z.uuid(),
});

export const updateGatewayValidator = z.object({
  id: z.uuid(),
  data: z.object({
    name: z.string().min(1).max(255).optional(),
    type: z.enum(["gateway", "label"]).optional(),
  }),
});

export const deleteGatewayValidator = z.object({
  id: z.uuid(),
});
