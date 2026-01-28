import "server-cli-only";

import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import type { GatewayLabelReport } from "@/services/gateway/gateway.input";
import { LabelRepository } from "@/services/gateway/label/label.repository";

/**
 * Label Service - Business logic for ESL label device management.
 * Handles label registration, product assignment, and gateway communication.
 */
export class LabelService {
  private readonly logger = new Logger("LabelService");
  private readonly repository = new LabelRepository();

  // ============================================================================
  // Label Serial Operations (Admin)
  // ============================================================================

  /**
   * Register a new label serial number (admin only).
   */
  async createSerial(params: { serialNumber: string; notes?: string }) {
    // Check if serial already exists
    const existing = await this.repository.readSerialByNumber({
      serialNumber: params.serialNumber,
    });

    if (existing) {
      const errorMessage = `Serial number "${params.serialNumber}" already exists.`;
      this.logger.error(`createSerial(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    const result = await this.repository.createSerial({
      serialNumber: params.serialNumber,
      notes: params.notes,
    });

    this.logger.debug(`createSerial(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all label serials (admin only).
   */
  async readAllSerials() {
    const result = await this.repository.readAllSerials();
    this.logger.debug(`readAllSerials() -> ${result.length} records`);
    return result;
  }

  // ============================================================================
  // Label Operations (User)
  // ============================================================================

  /**
   * Register a label device.
   * Creates a label in 'pending' status, waiting for a gateway to find it.
   */
  async register(params: {
    serialNumber: string;
    name: string;
    ownerId: string;
  }) {
    // Check if serial exists and is unclaimed
    const serial = await this.repository.readSerialByNumber({
      serialNumber: params.serialNumber,
    });

    if (!serial) {
      const errorMessage = `Serial number "${params.serialNumber}" is not valid.`;
      this.logger.error(`register(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    if (serial.isClaimed) {
      const errorMessage = `Serial number "${params.serialNumber}" has already been registered.`;
      this.logger.error(`register(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    // Create label record in pending status
    const label = await this.repository.create({
      name: params.name,
      serialNumber: params.serialNumber,
      ownerId: params.ownerId,
      status: "pending",
    });

    if (!label) {
      throw new Error("Failed to create label");
    }

    // Mark serial as claimed
    await this.repository.updateSerial({
      id: serial.id,
      data: {
        isClaimed: true,
        labelId: label.id,
        claimedAt: new Date(),
      },
    });

    this.logger.debug(`register(${jts(params)}) -> ${jts(label)}`);
    return label;
  }

  /**
   * Get a specific label by ID.
   */
  async read(params: { id: string; ownerId: string }) {
    const result = await this.repository.read(params);

    if (!result) {
      const errorMessage = `Label with ID "${params.id}" not found.`;
      this.logger.error(`read(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`read(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all labels for a user.
   */
  async readAll(params: { ownerId: string }) {
    const result = await this.repository.readAll(params);
    this.logger.debug(`readAll(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Update a label's settings.
   */
  async update(params: {
    id: string;
    ownerId: string;
    name?: string;
    productId?: string | null;
  }) {
    const result = await this.repository.update({
      id: params.id,
      ownerId: params.ownerId,
      data: {
        name: params.name,
        productId: params.productId,
      },
    });

    if (!result) {
      const errorMessage = `Label with ID "${params.id}" not found.`;
      this.logger.error(`update(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`update(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Assign a product to a label.
   */
  async assignProduct(params: {
    labelId: string;
    productId: string | null;
    ownerId: string;
  }) {
    const result = await this.repository.update({
      id: params.labelId,
      ownerId: params.ownerId,
      data: {
        productId: params.productId,
      },
    });

    if (!result) {
      const errorMessage = `Label with ID "${params.labelId}" not found.`;
      this.logger.error(`assignProduct(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`assignProduct(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Delete a label.
   */
  async delete(params: { id: string; ownerId: string }) {
    const result = await this.repository.delete(params);

    if (!result) {
      const errorMessage = `Label with ID "${params.id}" not found.`;
      this.logger.error(`delete(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`delete(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  // ============================================================================
  // Gateway Communication Methods
  // ============================================================================

  /**
   * Get labels in pending status that gateways should try to find.
   */
  async getPendingLabels(params: { ownerId: string }) {
    const result = await this.repository.readPending(params);
    this.logger.debug(
      `getPendingLabels(${jts(params)}) -> ${result.length} records`,
    );
    return result;
  }

  /**
   * Get labels connected to a gateway that need display updates.
   */
  async getLabelsNeedingUpdate(params: { gatewayId: string }) {
    const result = await this.repository.readNeedingUpdate(params);
    this.logger.debug(
      `getLabelsNeedingUpdate(${jts(params)}) -> ${result.length} records`,
    );
    return result;
  }

  /**
   * Process a label report from a gateway.
   * Updates label status, battery, and gateway connection.
   */
  async processGatewayReport(params: {
    gatewayId: string;
    ownerId: string;
    report: GatewayLabelReport;
  }) {
    // Find label by serial number
    const existingLabel = await this.repository.readBySerialNumber({
      serialNumber: params.report.serialNumber,
    });

    if (!existingLabel) {
      // Label not registered in our system, ignore
      this.logger.debug(
        `processGatewayReport: Unknown label ${params.report.serialNumber}`,
      );
      return null;
    }

    // Verify ownership
    if (existingLabel.ownerId !== params.ownerId) {
      this.logger.warn(
        `processGatewayReport: Label ${params.report.serialNumber} belongs to different owner`,
      );
      return null;
    }

    // Update label with gateway report data
    const result = await this.repository.updateBySerialNumber({
      serialNumber: params.report.serialNumber,
      data: {
        gatewayId: params.gatewayId,
        status: params.report.status,
        batteryPercent: params.report.batteryPercent,
        lastError: params.report.lastError,
        lastSeenAt: new Date(),
        displayWidth: params.report.displayWidth,
        displayHeight: params.report.displayHeight,
      },
    });

    this.logger.debug(`processGatewayReport(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Process the result of a label update attempt.
   */
  async processUpdateResult(params: {
    serialNumber: string;
    success: boolean;
    error?: string;
  }) {
    const result = await this.repository.updateBySerialNumber({
      serialNumber: params.serialNumber,
      data: {
        status: params.success ? "online" : "error",
        lastError: params.error,
        lastUpdateAt: params.success ? new Date() : undefined,
      },
    });

    this.logger.debug(`processUpdateResult(${jts(params)}) -> ${jts(result)}`);
    return result;
  }
}
