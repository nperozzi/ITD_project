import "server-cli-only";

import { db } from "@/database";
import { product } from "@/database/schema";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { and, eq } from "drizzle-orm";

/**
 * Repository for product database operations.
 * All database calls for products should go through this class.
 */
export class ProductRepository {
  private readonly logger = new Logger("ProductRepository");

  /**
   * Create a new product record
   */
  async create(params: typeof product.$inferInsert) {
    const result = (await db.insert(product).values(params).returning())[0];

    this.logger.debug(`create(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a product by ID and owner
   */
  async read(params: { id: string; ownerId: string }) {
    const result = await db.query.product.findFirst({
      where: and(
        eq(product.id, params.id),
        eq(product.ownerId, params.ownerId),
      ),
    });

    this.logger.debug(`read(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all products for an owner
   */
  async readAll(params: { ownerId: string }) {
    const result = await db.query.product.findMany({
      where: eq(product.ownerId, params.ownerId),
      orderBy: (p, { desc }) => [desc(p.createdAt)],
    });

    this.logger.debug(`readAll(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Get active products for an owner
   */
  async readActive(params: { ownerId: string }) {
    const result = await db.query.product.findMany({
      where: and(
        eq(product.ownerId, params.ownerId),
        eq(product.isActive, true),
      ),
      orderBy: (p, { asc }) => [asc(p.name)],
    });

    this.logger.debug(`readActive(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Find a product by barcode
   */
  async readByBarcode(params: { barcode: string; ownerId: string }) {
    const result = await db.query.product.findFirst({
      where: and(
        eq(product.barcode, params.barcode),
        eq(product.ownerId, params.ownerId),
      ),
    });

    this.logger.debug(`readByBarcode(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Update a product record
   */
  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof product.$inferInsert>;
  }) {
    const result = (
      await db
        .update(product)
        .set({ ...params.data, updatedAt: new Date() })
        .where(
          and(eq(product.id, params.id), eq(product.ownerId, params.ownerId)),
        )
        .returning()
    )[0];

    this.logger.debug(`update(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Delete a product record
   */
  async delete(params: { id: string; ownerId: string }) {
    const result = (
      await db
        .delete(product)
        .where(
          and(eq(product.id, params.id), eq(product.ownerId, params.ownerId)),
        )
        .returning()
    )[0];

    this.logger.debug(`delete(${jts(params)}) -> ${jts(result)}`);
    return result;
  }
}
