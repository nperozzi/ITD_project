import "server-cli-only";

import { db } from "@/database";
import { gateway, gatewaySerial } from "@/database/schema";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { and, eq } from "drizzle-orm";

/**
 * Repository for gateway and gateway serial database operations.
 * All database calls for gateways should go through this class.
 */
export class GatewayRepository {
  private readonly logger = new Logger("GatewayRepository");

  // ============================================================================
  // Gateway Serial Operations
  // ============================================================================

  /**
   * Create a new gateway serial number (admin only)
   */
  async createSerial(params: typeof gatewaySerial.$inferInsert) {
    const result = (
      await db.insert(gatewaySerial).values(params).returning()
    )[0];

    this.logger.debug(`createSerial(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a gateway serial by its serial number
   */
  async readSerialByNumber(params: { serialNumber: string }) {
    const result = await db.query.gatewaySerial.findFirst({
      where: eq(gatewaySerial.serialNumber, params.serialNumber),
    });

    this.logger.debug(`readSerialByNumber(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Update a gateway serial record
   */
  async updateSerial(params: {
    id: string;
    data: Partial<typeof gatewaySerial.$inferInsert>;
  }) {
    const result = (
      await db
        .update(gatewaySerial)
        .set(params.data)
        .where(eq(gatewaySerial.id, params.id))
        .returning()
    )[0];

    this.logger.debug(`updateSerial(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all gateway serials (admin only)
   */
  async readAllSerials() {
    const result = await db.query.gatewaySerial.findMany({
      orderBy: (serial, { desc }) => [desc(serial.createdAt)],
    });

    this.logger.debug(`readAllSerials() -> ${result.length} records`);
    return result;
  }

  // ============================================================================
  // Gateway Operations
  // ============================================================================

  /**
   * Create a new gateway record
   */
  async create(params: typeof gateway.$inferInsert) {
    const result = (await db.insert(gateway).values(params).returning())[0];

    this.logger.debug(`create(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a gateway by ID and owner
   */
  async read(params: { id: string; ownerId: string }) {
    const result = await db.query.gateway.findFirst({
      where: and(
        eq(gateway.id, params.id),
        eq(gateway.ownerId, params.ownerId),
      ),
      with: {
        labels: {
          with: {
            product: true,
          },
        },
      },
    });

    this.logger.debug(`read(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a gateway by serial number
   */
  async readBySerialNumber(params: { serialNumber: string }) {
    const result = await db.query.gateway.findFirst({
      where: eq(gateway.serialNumber, params.serialNumber),
    });

    this.logger.debug(`readBySerialNumber(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Find a gateway by API key (for gateway authentication)
   */
  async readByApiKey(params: { apiKey: string }) {
    const result = await db.query.gateway.findFirst({
      where: eq(gateway.apiKey, params.apiKey),
      with: {
        owner: true,
      },
    });

    this.logger.debug(
      `readByApiKey(${jts({ apiKey: "***" })}) -> ${result ? "found" : "not found"}`,
    );
    return result;
  }

  /**
   * Get all gateways for an owner
   */
  async readAll(params: { ownerId: string }) {
    const result = await db.query.gateway.findMany({
      where: eq(gateway.ownerId, params.ownerId),
      with: {
        labels: true,
      },
      orderBy: (g, { desc }) => [desc(g.createdAt)],
    });

    this.logger.debug(`readAll(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Update a gateway record
   */
  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof gateway.$inferInsert>;
  }) {
    const result = (
      await db
        .update(gateway)
        .set({ ...params.data, updatedAt: new Date() })
        .where(
          and(eq(gateway.id, params.id), eq(gateway.ownerId, params.ownerId)),
        )
        .returning()
    )[0];

    this.logger.debug(`update(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Update a gateway by API key (for gateway device updates)
   */
  async updateByApiKey(params: {
    apiKey: string;
    data: Partial<typeof gateway.$inferInsert>;
  }) {
    const result = (
      await db
        .update(gateway)
        .set({ ...params.data, updatedAt: new Date() })
        .where(eq(gateway.apiKey, params.apiKey))
        .returning()
    )[0];

    this.logger.debug(
      `updateByApiKey(${jts({ apiKey: "***", data: params.data })}) -> ${jts(result)}`,
    );
    return result;
  }

  /**
   * Delete a gateway record
   */
  async delete(params: { id: string; ownerId: string }) {
    const result = (
      await db
        .delete(gateway)
        .where(
          and(eq(gateway.id, params.id), eq(gateway.ownerId, params.ownerId)),
        )
        .returning()
    )[0];

    this.logger.debug(`delete(${jts(params)}) -> ${jts(result)}`);
    return result;
  }
}
