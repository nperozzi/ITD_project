import "server-cli-only";

import { db } from "@/database";
import { label } from "@/database/schema";
import Logger from "@/lib/logger";
import { and, eq } from "drizzle-orm";

export class LabelRepository {
  logger = new Logger(LabelRepository.name);
  constructor() {}

  async create(params: typeof label.$inferInsert) {
    return (
      await db
        .insert(label)
        .values({
          ...params,
        })
        .returning()
    )[0];
  }

  async read(params: { id: string; ownerId: string }) {
    return await db.query.label.findFirst({
      where: and(eq(label.id, params.id), eq(label.ownerId, params.ownerId)),
    });
  }
  async readAll(params: { ownerId: string }) {
    return await db.query.label.findMany({
      where: eq(label.ownerId, params.ownerId),
    });
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof label.$inferInsert>;
  }) {
    return (
      await db
        .update(label)
        .set({
          ...params.data,
        })
        .where(and(eq(label.id, params.id), eq(label.ownerId, params.ownerId)))
        .returning()
    )[0];
  }

  async delete(params: { id: string; ownerId: string }) {
    return (
      await db
        .delete(label)
        .where(and(eq(label.id, params.id), eq(label.ownerId, params.ownerId)))
        .returning()
    )[0];
  }
}
