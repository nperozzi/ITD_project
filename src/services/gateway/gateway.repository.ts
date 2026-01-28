import "server-cli-only";

import { db } from "@/database";
import { gateway } from "@/database/schema";
import Logger from "@/lib/logger";
import { and, eq } from "drizzle-orm";

export class GatewayRepository {
  logger = new Logger(GatewayRepository.name);
  constructor() {}

  async create(params: typeof gateway.$inferInsert) {
    return (
      await db
        .insert(gateway)
        .values({
          ...params,
        })
        .returning()
    )[0];
  }

  async read(params: { id: string; ownerId: string }) {
    return await db.query.gateway.findFirst({
      where: and(
        eq(gateway.id, params.id),
        eq(gateway.ownerId, params.ownerId),
      ),
    });
  }
  async readAll(params: { ownerId: string }) {
    return await db.query.gateway.findMany({
      where: eq(gateway.ownerId, params.ownerId),
    });
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof gateway.$inferInsert>;
  }) {
    return (
      await db
        .update(gateway)
        .set({
          ...params.data,
        })
        .where(
          and(eq(gateway.id, params.id), eq(gateway.ownerId, params.ownerId)),
        )
        .returning()
    )[0];
  }

  async delete(params: { id: string; ownerId: string }) {
    return (
      await db
        .delete(gateway)
        .where(
          and(eq(gateway.id, params.id), eq(gateway.ownerId, params.ownerId)),
        )
        .returning()
    )[0];
  }
}
