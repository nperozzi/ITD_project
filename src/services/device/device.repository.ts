import "server-cli-only";

import { db } from "@/database";
import { device } from "@/database/schema";
import Logger from "@/lib/logger";
import { and, eq } from "drizzle-orm";

export class DeviceRepository {
  logger = new Logger(DeviceRepository.name);
  constructor() {}

  async create(params: typeof device.$inferInsert) {
    return (
      await db
        .insert(device)
        .values({
          ...params,
        })
        .returning()
    )[0];
  }

  async read(params: { id: string; ownerId: string }) {
    return await db.query.device.findFirst({
      where: and(eq(device.id, params.id), eq(device.ownerId, params.ownerId)),
    });
  }
  async readAll(params: { ownerId: string }) {
    return await db.query.device.findMany({
      where: eq(device.ownerId, params.ownerId),
    });
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof device.$inferInsert>;
  }) {
    return (
      await db
        .update(device)
        .set({
          ...params.data,
        })
        .where(
          and(eq(device.id, params.id), eq(device.ownerId, params.ownerId)),
        )
        .returning()
    )[0];
  }

  async delete(params: { id: string; ownerId: string }) {
    return (
      await db
        .delete(device)
        .where(
          and(eq(device.id, params.id), eq(device.ownerId, params.ownerId)),
        )
        .returning()
    )[0];
  }
}
