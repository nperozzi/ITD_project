/**
 * ESL Gateway API End-to-End Tests
 *
 * These tests verify the complete flow of the gateway and label system:
 * 1. Admin creates serial numbers
 * 2. User claims gateway
 * 3. Gateway checks claim status
 * 4. Gateway syncs labels
 * 5. Labels receive updates
 *
 * Run with: bun test tests/e2e/gateway-api.test.ts
 */

import { db } from "@/database";
import {
  gateway,
  gatewaySerial,
  label,
  labelSerial,
  product,
  user,
} from "@/database/schema";
import { gatewayService } from "@/services/gateway/gateway.service";
import type { ProductPriceDetails } from "@/services/product/product.schema";
import { productService } from "@/services/product/product.service";
import { afterAll, beforeAll, describe, expect, it } from "bun:test";
import { eq } from "drizzle-orm";

const BASE_URL = process.env.TEST_BASE_URL || "http://localhost:3000";

// Test data
const TEST_USER_ID = "test-user-e2e-" + Date.now();
const TEST_GATEWAY_SERIAL = "GW-E2E-TEST-" + Date.now();
const TEST_LABEL_SERIAL = "ESL-E2E-TEST-" + Date.now();

let testGatewayId: string;
let testGatewayApiKey: string;
let testLabelId: string;
let testProductId: string;

describe("Gateway API E2E Tests", () => {
  // ============================================================================
  // Setup
  // ============================================================================

  beforeAll(async () => {
    // Create test user (simulated - in real test you'd use auth)
    await db.insert(user).values({
      id: TEST_USER_ID,
      email: "e2e-test@example.com",
      name: "E2E Test User",
      emailVerified: true,
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    console.log("✓ Test user created:", TEST_USER_ID);
  });

  afterAll(async () => {
    // Clean up test data
    await db.delete(label).where(eq(label.ownerId, TEST_USER_ID));
    await db.delete(gateway).where(eq(gateway.ownerId, TEST_USER_ID));
    await db.delete(product).where(eq(product.ownerId, TEST_USER_ID));
    await db
      .delete(gatewaySerial)
      .where(eq(gatewaySerial.serialNumber, TEST_GATEWAY_SERIAL));
    await db
      .delete(labelSerial)
      .where(eq(labelSerial.serialNumber, TEST_LABEL_SERIAL));
    await db.delete(user).where(eq(user.id, TEST_USER_ID));

    console.log("✓ Test data cleaned up");
  });

  // ============================================================================
  // Test: Admin Creates Gateway Serial
  // ============================================================================

  describe("1. Admin Creates Gateway Serial", () => {
    it("should create a gateway serial number", async () => {
      const result = await gatewayService.createSerial({
        serialNumber: TEST_GATEWAY_SERIAL,
      });

      expect(result).toBeDefined();
      expect(result.serialNumber).toBe(TEST_GATEWAY_SERIAL);
      expect(result.isClaimed).toBe(false);
      expect(result.gatewayId).toBeNull();

      console.log("✓ Gateway serial created:", TEST_GATEWAY_SERIAL);
    });

    it("should reject duplicate serial numbers", async () => {
      await expect(
        gatewayService.createSerial({
          serialNumber: TEST_GATEWAY_SERIAL,
        }),
      ).rejects.toThrow(/already exists/i);
    });
  });

  // ============================================================================
  // Test: Gateway Checks Claim Status (Before Claim)
  // ============================================================================

  describe("2. Gateway Checks Unclaimed Status", () => {
    it("should return unclaimed status via API", async () => {
      const response = await fetch(
        `${BASE_URL}/api/gateway/claim?serial=${TEST_GATEWAY_SERIAL}`,
      );

      expect(response.ok).toBe(true);
      const data = await response.json();

      expect(data.status).toBe("unclaimed");
      expect(data.apiKey).toBeUndefined();

      console.log("✓ Claim check returned unclaimed status");
    });

    it("should return invalid for unknown serial", async () => {
      const response = await fetch(
        `${BASE_URL}/api/gateway/claim?serial=INVALID-SERIAL-123`,
      );

      expect(response.ok).toBe(true);
      const data = await response.json();

      expect(data.status).toBe("invalid");
    });

    it("should return error for missing serial", async () => {
      const response = await fetch(`${BASE_URL}/api/gateway/claim`);

      expect(response.status).toBe(400);
    });
  });

  // ============================================================================
  // Test: User Claims Gateway
  // ============================================================================

  describe("3. User Claims Gateway", () => {
    it("should claim gateway with valid serial", async () => {
      const result = await gatewayService.claim({
        serialNumber: TEST_GATEWAY_SERIAL,
        name: "E2E Test Gateway",
        ownerId: TEST_USER_ID,
      });

      expect(result).toBeDefined();
      expect(result.name).toBe("E2E Test Gateway");
      expect(result.serialNumber).toBe(TEST_GATEWAY_SERIAL);
      expect(result.ownerId).toBe(TEST_USER_ID);
      expect(result.apiKey).toMatch(/^gw_/);

      testGatewayId = result.id;
      testGatewayApiKey = result.apiKey;

      console.log("✓ Gateway claimed:", testGatewayId);
      console.log(
        "✓ API Key received:",
        testGatewayApiKey.substring(0, 20) + "...",
      );
    });

    it("should reject already claimed serial", async () => {
      await expect(
        gatewayService.claim({
          serialNumber: TEST_GATEWAY_SERIAL,
          name: "Another Gateway",
          ownerId: TEST_USER_ID,
        }),
      ).rejects.toThrow(/already been claimed/i);
    });
  });

  // ============================================================================
  // Test: Gateway Checks Claim Status (After Claim)
  // ============================================================================

  describe("4. Gateway Checks Claimed Status", () => {
    it("should return claimed status with API key", async () => {
      const response = await fetch(
        `${BASE_URL}/api/gateway/claim?serial=${TEST_GATEWAY_SERIAL}`,
      );

      expect(response.ok).toBe(true);
      const data = await response.json();

      expect(data.status).toBe("claimed");
      expect(data.apiKey).toBe(testGatewayApiKey);
      expect(data.gatewayId).toBe(testGatewayId);
      expect(data.ownerId).toBe(TEST_USER_ID);
      expect(data.name).toBe("E2E Test Gateway");

      console.log("✓ Claim check returned claimed status with API key");
    });
  });

  // ============================================================================
  // Test: Admin Creates Label Serial
  // ============================================================================

  describe("5. Admin Creates Label Serial", () => {
    it("should create a label serial number", async () => {
      const result = await gatewayService.label.createSerial({
        serialNumber: TEST_LABEL_SERIAL,
      });

      expect(result).toBeDefined();
      expect(result.serialNumber).toBe(TEST_LABEL_SERIAL);
      expect(result.isRegistered).toBe(false);

      console.log("✓ Label serial created:", TEST_LABEL_SERIAL);
    });
  });

  // ============================================================================
  // Test: User Registers Label
  // ============================================================================

  describe("6. User Registers Label", () => {
    it("should register label with valid serial", async () => {
      const result = await gatewayService.label.register({
        serialNumber: TEST_LABEL_SERIAL,
        name: "E2E Test Label",
        ownerId: TEST_USER_ID,
      });

      expect(result).toBeDefined();
      expect(result.name).toBe("E2E Test Label");
      expect(result.serialNumber).toBe(TEST_LABEL_SERIAL);
      expect(result.status).toBe("pending");

      testLabelId = result.id;

      console.log("✓ Label registered:", testLabelId);
    });
  });

  // ============================================================================
  // Test: User Creates Product
  // ============================================================================

  describe("7. User Creates Product", () => {
    it("should create a product with price details", async () => {
      const priceDetails: ProductPriceDetails = {
        currency: {
          code: "SEK",
          symbol: { suffix: " kr" },
          decimalPlaces: 2,
        },
        priceInCents: 8990,
        priceUnit: "kg",
        quantity: 1,
        quantityUnit: "kg",
        discount: {
          percentage: 20,
          validUntil: "2025-12-31",
        },
      };

      const result = await productService.create({
        ownerId: TEST_USER_ID,
        name: "E2E Test Chicken",
        brand: "Test Farm",
        barcode: "7350123456789",
        sku: "E2E-CHK-001",
        priceDetails,
      });

      expect(result).toBeDefined();
      expect(result.name).toBe("E2E Test Chicken");
      expect(result.barcode).toBe("7350123456789");

      testProductId = result.id;

      console.log("✓ Product created:", testProductId);
    });
  });

  // ============================================================================
  // Test: User Assigns Product to Label
  // ============================================================================

  describe("8. User Assigns Product to Label", () => {
    it("should assign product to label", async () => {
      const result = await gatewayService.label.assignProduct({
        labelId: testLabelId,
        productId: testProductId,
        ownerId: TEST_USER_ID,
      });

      expect(result).toBeDefined();
      expect(result.productId).toBe(testProductId);
      expect(result.needsUpdate).toBe(true);

      console.log("✓ Product assigned to label");
    });
  });

  // ============================================================================
  // Test: Gateway Syncs Labels
  // ============================================================================

  describe("9. Gateway Syncs Labels", () => {
    it("should sync labels and receive updates", async () => {
      const response = await fetch(`${BASE_URL}/api/gateway/sync`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${testGatewayApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          firmwareVersion: "1.0.0-e2e",
          labels: [
            {
              serialNumber: TEST_LABEL_SERIAL,
              batteryPercent: 95,
              rssi: -40,
              firmwareVersion: "2.0.0-e2e",
            },
          ],
        }),
      });

      expect(response.ok).toBe(true);
      const data = await response.json();

      expect(data.success).toBe(true);
      expect(data.gateway).toBeDefined();
      expect(data.gateway.id).toBe(testGatewayId);
      expect(data.labels.connected).toBeGreaterThanOrEqual(1);
      expect(data.updates).toBeDefined();
      expect(data.updates.length).toBeGreaterThanOrEqual(1);

      // Check update contains product data
      const update = data.updates[0];
      expect(update.serialNumber).toBe(TEST_LABEL_SERIAL);
      expect(update.product).toBeDefined();
      expect(update.product.name).toBe("E2E Test Chicken");
      expect(update.product.priceDetails.priceInCents).toBe(8990);
      expect(update.product.priceDetails.discount.percentage).toBe(20);

      console.log("✓ Sync returned", data.updates.length, "update(s)");
      console.log("✓ Product data in update:", update.product.name);
    });

    it("should reject sync without auth", async () => {
      const response = await fetch(`${BASE_URL}/api/gateway/sync`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          labels: [],
        }),
      });

      expect(response.status).toBe(401);
    });

    it("should reject sync with invalid auth", async () => {
      const response = await fetch(`${BASE_URL}/api/gateway/sync`, {
        method: "POST",
        headers: {
          Authorization: "Bearer invalid-key",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          labels: [],
        }),
      });

      expect(response.status).toBe(401);
    });
  });

  // ============================================================================
  // Test: Gateway Acknowledges Updates
  // ============================================================================

  describe("10. Gateway Acknowledges Updates", () => {
    it("should acknowledge successful update", async () => {
      const response = await fetch(`${BASE_URL}/api/gateway/sync`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${testGatewayApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          results: [
            {
              labelId: testLabelId,
              success: true,
            },
          ],
        }),
      });

      expect(response.ok).toBe(true);
      const data = await response.json();

      expect(data.success).toBe(true);
      expect(data.processed).toBe(1);
      expect(data.successful).toBe(1);
      expect(data.failed).toBe(0);

      console.log("✓ Update acknowledgment processed");
    });

    it("should handle failed update acknowledgment", async () => {
      // First, assign product again to trigger needsUpdate
      await gatewayService.label.assignProduct({
        labelId: testLabelId,
        productId: testProductId,
        ownerId: TEST_USER_ID,
      });

      const response = await fetch(`${BASE_URL}/api/gateway/sync`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${testGatewayApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          results: [
            {
              labelId: testLabelId,
              success: false,
              error: "E2E test error",
            },
          ],
        }),
      });

      expect(response.ok).toBe(true);
      const data = await response.json();

      expect(data.success).toBe(true);
      expect(data.failed).toBe(1);

      console.log("✓ Failed update acknowledgment handled");
    });
  });

  // ============================================================================
  // Test: Label Status Updates
  // ============================================================================

  describe("11. Label Status Verification", () => {
    it("should have label connected to gateway", async () => {
      const labelData = await gatewayService.label.read({
        id: testLabelId,
        ownerId: TEST_USER_ID,
      });

      expect(labelData).toBeDefined();
      expect(labelData?.gatewayId).toBe(testGatewayId);
      expect(labelData?.status).toBe("online");
      expect(labelData?.batteryPercent).toBe(95);

      console.log("✓ Label status verified: online with gateway connection");
    });
  });

  // ============================================================================
  // Test: Gateway Online Status
  // ============================================================================

  describe("12. Gateway Online Status", () => {
    it("should have gateway marked as online after sync", async () => {
      const gatewayData = await gatewayService.read({
        id: testGatewayId,
        ownerId: TEST_USER_ID,
      });

      expect(gatewayData).toBeDefined();
      expect(gatewayData?.isOnline).toBe(true);
      expect(gatewayData?.firmwareVersion).toBe("1.0.0-e2e");
      expect(gatewayData?.lastPingAt).toBeDefined();

      console.log(
        "✓ Gateway status verified: online with firmware",
        gatewayData?.firmwareVersion,
      );
    });
  });
});

// ============================================================================
// Additional Integration Tests
// ============================================================================

describe("Gateway Service Integration Tests", () => {
  const INTEGRATION_USER_ID = "test-integration-" + Date.now();
  const INTEGRATION_SERIAL = "GW-INT-" + Date.now();

  beforeAll(async () => {
    await db.insert(user).values({
      id: INTEGRATION_USER_ID,
      email: "integration@example.com",
      name: "Integration Test",
      emailVerified: true,
      createdAt: new Date(),
      updatedAt: new Date(),
    });
  });

  afterAll(async () => {
    await db.delete(gateway).where(eq(gateway.ownerId, INTEGRATION_USER_ID));
    await db
      .delete(gatewaySerial)
      .where(eq(gatewaySerial.serialNumber, INTEGRATION_SERIAL));
    await db.delete(user).where(eq(user.id, INTEGRATION_USER_ID));
  });

  it("should handle complete claim flow", async () => {
    // Step 1: Create serial
    const serial = await gatewayService.createSerial({
      serialNumber: INTEGRATION_SERIAL,
    });
    expect(serial.isClaimed).toBe(false);

    // Step 2: Check status (unclaimed)
    const statusBefore = await gatewayService.checkSerialStatus({
      serialNumber: INTEGRATION_SERIAL,
    });
    expect(statusBefore.status).toBe("unclaimed");

    // Step 3: Claim
    const claimed = await gatewayService.claim({
      serialNumber: INTEGRATION_SERIAL,
      name: "Integration Gateway",
      ownerId: INTEGRATION_USER_ID,
    });
    expect(claimed.apiKey).toMatch(/^gw_/);

    // Step 4: Check status (claimed)
    const statusAfter = await gatewayService.checkSerialStatus({
      serialNumber: INTEGRATION_SERIAL,
    });
    expect(statusAfter.status).toBe("claimed");
    expect(statusAfter.apiKey).toBe(claimed.apiKey);

    // Step 5: Verify auth
    const authenticated = await gatewayService.authenticateByApiKey({
      apiKey: claimed.apiKey,
    });
    expect(authenticated?.id).toBe(claimed.id);

    console.log("✓ Complete claim flow verified");
  });

  it("should handle batch serial creation", async () => {
    const prefix = "GW-BATCH-INT-";
    const count = 5;

    const serials: string[] = [];
    for (let i = 0; i < count; i++) {
      const serial = await gatewayService.createSerial({
        serialNumber: `${prefix}${Date.now()}-${i}`,
      });
      serials.push(serial.serialNumber);
    }

    expect(serials.length).toBe(count);

    // Clean up
    for (const serial of serials) {
      await db
        .delete(gatewaySerial)
        .where(eq(gatewaySerial.serialNumber, serial));
    }

    console.log("✓ Batch serial creation verified");
  });
});
