import "server-cli-only";

import { db } from "@/database";
import { label, labelSerial } from "@/database/schema";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { and, eq } from "drizzle-orm";

/**
 * Repository for label and label serial database operations.
 * All database calls for labels should go through this class.
 */
export class LabelRepository {
  private readonly logger = new Logger("LabelRepository");

  // ============================================================================
  // Label Serial Operations
  // ============================================================================

  /**
   * Create a new label serial number (admin only)
   */
  async createSerial(params: typeof labelSerial.$inferInsert) {
    const result = (await db.insert(labelSerial).values(params).returning())[0];

    this.logger.debug(`createSerial(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a label serial by its serial number
   */
  async readSerialByNumber(params: { serialNumber: string }) {
    const result = await db.query.labelSerial.findFirst({
      where: eq(labelSerial.serialNumber, params.serialNumber),
    });

    this.logger.debug(`readSerialByNumber(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Update a label serial record
   */
  async updateSerial(params: {
    id: string;
    data: Partial<typeof labelSerial.$inferInsert>;
  }) {
    const result = (
      await db
        .update(labelSerial)
        .set(params.data)
        .where(eq(labelSerial.id, params.id))
        .returning()
    )[0];

    this.logger.debug(`updateSerial(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all label serials (admin only)
   */
  async readAllSerials() {
    const result = await db.query.labelSerial.findMany({
      orderBy: (serial, { desc }) => [desc(serial.createdAt)],
    });

    this.logger.debug(`readAllSerials() -> ${result.length} records`);
    return result;
  }

  // ============================================================================
  // Label Operations
  // ============================================================================

  /**
   * Create a new label record
   */
  async create(params: typeof label.$inferInsert) {
    const result = (await db.insert(label).values(params).returning())[0];

    this.logger.debug(`create(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a label by ID and owner
   */
  async read(params: { id: string; ownerId: string }) {
    const result = await db.query.label.findFirst({
      where: and(eq(label.id, params.id), eq(label.ownerId, params.ownerId)),
      with: {
        product: true,
        gateway: true,
      },
    });

    this.logger.debug(`read(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a label by serial number
   */
  async readBySerialNumber(params: { serialNumber: string }) {
    const result = await db.query.label.findFirst({
      where: eq(label.serialNumber, params.serialNumber),
      with: {
        product: true,
        gateway: true,
      },
    });

    this.logger.debug(`readBySerialNumber(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all labels for an owner
   */
  async readAll(params: { ownerId: string }) {
    const result = await db.query.label.findMany({
      where: eq(label.ownerId, params.ownerId),
      with: {
        product: true,
        gateway: true,
      },
      orderBy: (l, { desc }) => [desc(l.createdAt)],
    });

    this.logger.debug(`readAll(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Get labels in pending status (waiting for gateway to find them)
   */
  async readPending(params: { ownerId: string }) {
    const result = await db.query.label.findMany({
      where: and(
        eq(label.ownerId, params.ownerId),
        eq(label.status, "pending"),
      ),
      with: {
        product: true,
      },
    });

    this.logger.debug(
      `readPending(${jts(params)}) -> ${result.length} records`,
    );
    return result;
  }

  /**
   * Get labels connected to a specific gateway that have pending product updates
   */
  async readNeedingUpdate(params: { gatewayId: string }) {
    const result = await db.query.label.findMany({
      where: and(
        eq(label.gatewayId, params.gatewayId),
        eq(label.status, "online"),
      ),
      with: {
        product: true,
      },
    });

    // Filter to labels that have a product assigned
    const labelsWithProducts = result.filter((l) => l.productId !== null);

    this.logger.debug(
      `readNeedingUpdate(${jts(params)}) -> ${labelsWithProducts.length} records`,
    );
    return labelsWithProducts;
  }

  /**
   * Update a label record
   */
  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof label.$inferInsert>;
  }) {
    const result = (
      await db
        .update(label)
        .set({ ...params.data, updatedAt: new Date() })
        .where(and(eq(label.id, params.id), eq(label.ownerId, params.ownerId)))
        .returning()
    )[0];

    this.logger.debug(`update(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Update a label by serial number
   */
  async updateBySerialNumber(params: {
    serialNumber: string;
    data: Partial<typeof label.$inferInsert>;
  }) {
    const result = (
      await db
        .update(label)
        .set({ ...params.data, updatedAt: new Date() })
        .where(eq(label.serialNumber, params.serialNumber))
        .returning()
    )[0];

    this.logger.debug(`updateBySerialNumber(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Delete a label record
   */
  async delete(params: { id: string; ownerId: string }) {
    const result = (
      await db
        .delete(label)
        .where(and(eq(label.id, params.id), eq(label.ownerId, params.ownerId)))
        .returning()
    )[0];

    this.logger.debug(`delete(${jts(params)}) -> ${jts(result)}`);
    return result;
  }
}
