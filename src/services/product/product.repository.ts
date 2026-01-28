import "server-cli-only";

import { db } from "@/database";
import { product } from "@/database/schema";
import Logger from "@/lib/logger";
import { and, eq } from "drizzle-orm";

export class ProductRepository {
  logger = new Logger(ProductRepository.name);
  constructor() {}

  async create(params: typeof product.$inferInsert) {
    return (
      await db
        .insert(product)
        .values({
          ...params,
        })
        .returning()
    )[0];
  }

  async read(params: { id: string; ownerId: string }) {
    return await db.query.product.findFirst({
      where: and(
        eq(product.id, params.id),
        eq(product.ownerId, params.ownerId),
      ),
    });
  }
  async readAll(params: { ownerId: string }) {
    return await db.query.product.findMany({
      where: eq(product.ownerId, params.ownerId),
    });
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof product.$inferInsert>;
  }) {
    return (
      await db
        .update(product)
        .set({
          ...params.data,
        })
        .where(
          and(eq(product.id, params.id), eq(product.ownerId, params.ownerId)),
        )
        .returning()
    )[0];
  }

  async delete(params: { id: string; ownerId: string }) {
    return (
      await db
        .delete(product)
        .where(
          and(eq(product.id, params.id), eq(product.ownerId, params.ownerId)),
        )
        .returning()
    )[0];
  }
}
