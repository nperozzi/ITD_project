import "server-cli-only";

import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import type {
  GatewayAckInput,
  GatewaySyncInput,
} from "@/services/gateway/gateway.input";
import { GatewayRepository } from "@/services/gateway/gateway.repository";
import { LabelService } from "@/services/gateway/label/label.service";

/**
 * Generates a secure API key for gateway authentication.
 * Format: gw_<32 random hex characters>
 */
function generateApiKey(): string {
  const randomBytes = crypto.getRandomValues(new Uint8Array(16));
  const hex = Array.from(randomBytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return `gw_${hex}`;
}

/**
 * Gateway Service - Business logic for gateway and serial number management.
 * Handles the complete lifecycle from serial registration to gateway claiming and sync.
 */
class GatewayService {
  private readonly logger = new Logger("GatewayService");
  private readonly repository = new GatewayRepository();

  /** Sub-service for label operations */
  public readonly label = new LabelService();

  // ============================================================================
  // Gateway Serial Operations (Admin)
  // ============================================================================

  /**
   * Register a new gateway serial number (admin only).
   * This is like adding a gift card to the system that can be redeemed later.
   */
  async createSerial(params: { serialNumber: string; notes?: string }) {
    // Check if serial already exists
    const existing = await this.repository.readSerialByNumber({
      serialNumber: params.serialNumber.toLowerCase(),
    });

    if (existing) {
      const errorMessage = `Serial number "${params.serialNumber}" already exists.`;
      this.logger.error(`createSerial(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    const result = await this.repository.createSerial({
      serialNumber: params.serialNumber.toLowerCase(),
      notes: params.notes,
    });

    this.logger.debug(`createSerial(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Check if a serial number is valid and whether it has been claimed.
   * Used by gateway devices to check their claim status.
   */
  async checkSerialStatus(params: { serialNumber: string }) {
    const serial = await this.repository.readSerialByNumber({
      serialNumber: params.serialNumber.toLowerCase(),
    });

    if (!serial) {
      this.logger.debug(
        `checkSerialStatus(${jts(params)}) -> Serial not found`,
      );
      return { valid: false, claimed: false, gateway: null };
    }

    if (serial.isClaimed && serial.gatewayId) {
      const gateway = await this.repository.readBySerialNumber({
        serialNumber: params.serialNumber.toLowerCase(),
      });

      this.logger.debug(
        `checkSerialStatus(${jts(params)}) -> Claimed by gateway ${gateway?.id}`,
      );
      return {
        valid: true,
        claimed: true,
        gateway: gateway
          ? {
              id: gateway.id,
              apiKey: gateway.apiKey,
              name: gateway.name,
              ownerId: gateway.ownerId,
            }
          : null,
      };
    }

    this.logger.debug(
      `checkSerialStatus(${jts(params)}) -> Valid, not claimed`,
    );
    return { valid: true, claimed: false, gateway: null };
  }

  /**
   * Get all gateway serials (admin only).
   */
  async readAllSerials() {
    const result = await this.repository.readAllSerials();
    this.logger.debug(`readAllSerials() -> ${result.length} records`);
    return result;
  }

  // ============================================================================
  // Gateway Operations (User)
  // ============================================================================

  /**
   * Claim a gateway using a serial number.
   * This "redeems" the serial and creates a gateway record for the user.
   */
  async claim(params: { serialNumber: string; name: string; ownerId: string }) {
    // Check if serial exists and is unclaimed
    const serial = await this.repository.readSerialByNumber({
      serialNumber: params.serialNumber.toLowerCase(),
    });

    if (!serial) {
      const errorMessage = `Serial number "${params.serialNumber}" is not valid.`;
      this.logger.error(`claim(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    if (serial.isClaimed) {
      const errorMessage = `Serial number "${params.serialNumber}" has already been claimed.`;
      this.logger.error(`claim(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    // Generate API key for gateway authentication
    const apiKey = generateApiKey();

    // Create gateway record
    const gateway = await this.repository.create({
      name: params.name,
      serialNumber: params.serialNumber.toLowerCase(),
      ownerId: params.ownerId,
      apiKey,
    });

    if (!gateway) {
      throw new Error("Failed to create gateway");
    }

    // Mark serial as claimed
    await this.repository.updateSerial({
      id: serial.id,
      data: {
        isClaimed: true,
        gatewayId: gateway.id,
        claimedAt: new Date(),
      },
    });

    this.logger.debug(`claim(${jts(params)}) -> ${jts(gateway)}`);
    return gateway;
  }

  /**
   * Get a specific gateway by ID.
   */
  async read(params: { id: string; ownerId: string }) {
    const result = await this.repository.read(params);

    if (!result) {
      const errorMessage = `Gateway with ID "${params.id}" not found.`;
      this.logger.error(`read(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`read(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all gateways for a user.
   */
  async readAll(params: { ownerId: string }) {
    const result = await this.repository.readAll(params);
    this.logger.debug(`readAll(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Update a gateway's settings.
   */
  async update(params: { id: string; ownerId: string; name?: string }) {
    const result = await this.repository.update({
      id: params.id,
      ownerId: params.ownerId,
      data: { name: params.name },
    });

    if (!result) {
      const errorMessage = `Gateway with ID "${params.id}" not found.`;
      this.logger.error(`update(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`update(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Delete a gateway and release its serial for re-use.
   */
  async delete(params: { id: string; ownerId: string }) {
    // Get gateway first to find serial
    const existing = await this.repository.read(params);
    if (!existing) {
      const errorMessage = `Gateway with ID "${params.id}" not found.`;
      this.logger.error(`delete(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    // Delete gateway
    const result = await this.repository.delete(params);

    // Mark serial as unclaimed so it can be re-used
    const serial = await this.repository.readSerialByNumber({
      serialNumber: existing.serialNumber,
    });

    if (serial) {
      await this.repository.updateSerial({
        id: serial.id,
        data: {
          isClaimed: false,
          gatewayId: null,
          claimedAt: null,
        },
      });
      this.logger.debug(
        `delete(${jts(params)}): Serial ${existing.serialNumber} marked as unclaimed`,
      );
    }

    this.logger.debug(`delete(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  // ============================================================================
  // Gateway Device API Operations
  // ============================================================================

  /**
   * Authenticate a gateway by API key.
   * Returns the gateway if valid, null otherwise.
   */
  async authenticateByApiKey(params: { apiKey: string }) {
    const result = await this.repository.readByApiKey(params);
    this.logger.debug(
      `authenticateByApiKey() -> ${result ? "authenticated" : "failed"}`,
    );
    return result;
  }

  /**
   * Process a sync request from a gateway device.
   * Updates gateway status and processes label reports.
   * Returns instructions for the gateway (e.g., pending label registrations).
   */
  async sync(params: { apiKey: string; data: GatewaySyncInput }): Promise<{
    success: boolean;
    pendingLabels: Array<{
      serialNumber: string;
      productData: unknown;
    }>;
    labelsToUpdate: Array<{
      serialNumber: string;
      productData: unknown;
    }>;
  }> {
    // Authenticate gateway
    const gateway = await this.repository.readByApiKey({
      apiKey: params.apiKey,
    });

    if (!gateway) {
      const errorMessage = "Invalid API key.";
      this.logger.error(`sync(): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    // Update gateway status
    await this.repository.updateByApiKey({
      apiKey: params.apiKey,
      data: {
        isOnline: true,
        lastPingAt: new Date(),
        firmwareVersion: params.data.firmwareVersion,
        ipAddress: params.data.ipAddress,
      },
    });

    // Process label reports
    for (const labelReport of params.data.labels) {
      await this.label.processGatewayReport({
        gatewayId: gateway.id,
        ownerId: gateway.ownerId,
        report: labelReport,
      });
    }

    // Get pending labels that need to be found by this gateway
    const pendingLabels = await this.label.getPendingLabels({
      ownerId: gateway.ownerId,
    });

    // Get labels that need display updates
    const labelsToUpdate = await this.label.getLabelsNeedingUpdate({
      gatewayId: gateway.id,
    });

    this.logger.debug(
      `sync() -> pendingLabels: ${pendingLabels.length}, labelsToUpdate: ${labelsToUpdate.length}`,
    );

    return {
      success: true,
      pendingLabels: pendingLabels.map((l) => ({
        serialNumber: l.serialNumber,
        productData: l.product,
      })),
      labelsToUpdate: labelsToUpdate.map((l) => ({
        serialNumber: l.serialNumber,
        productData: l.product,
      })),
    };
  }

  /**
   * Process acknowledgment from gateway about label updates.
   */
  async acknowledge(params: { apiKey: string; data: GatewayAckInput }) {
    // Authenticate gateway
    const gateway = await this.repository.readByApiKey({
      apiKey: params.apiKey,
    });

    if (!gateway) {
      const errorMessage = "Invalid API key.";
      this.logger.error(`acknowledge(): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    // Process each result
    for (const result of params.data.results) {
      await this.label.processUpdateResult({
        serialNumber: result.labelSerialNumber,
        success: result.success,
        error: result.error,
      });
    }

    this.logger.debug(
      `acknowledge() -> Processed ${params.data.results.length} results`,
    );
    return { success: true };
  }
}

export const gatewayService = new GatewayService();
