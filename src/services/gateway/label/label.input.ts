import z from "zod";

export const createLabelValidator = z.object({
  name: z.string().min(1).max(255),
  type: z.enum(["gateway", "label"]),
});

export const readLabelValidator = z.object({
  id: z.uuid(),
});

export const updateLabelValidator = z.object({
  id: z.uuid(),
  data: z.object({
    name: z.string().min(1).max(255).optional(),
    type: z.enum(["gateway", "label"]).optional(),
  }),
});

export const deleteLabelValidator = z.object({
  id: z.uuid(),
});
