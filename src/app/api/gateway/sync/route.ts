import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import {
  gatewayAckValidator,
  gatewaySyncValidator,
} from "@/services/gateway/gateway.input";
import { gatewayService } from "@/services/gateway/gateway.service";
import { NextRequest, NextResponse } from "next/server";

const logger = new Logger("GatewaySyncAPI");

/**
 * Extract API key from Authorization header
 */
function extractApiKey(request: NextRequest): string | null {
  const authHeader = request.headers.get("Authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return null;
  }
  return authHeader.substring(7); // Remove "Bearer " prefix
}

/**
 * Gateway Sync API
 *
 * This endpoint is used by claimed gateway devices to sync data with the server.
 * The gateway should call this endpoint periodically (e.g., every 30 seconds).
 *
 * @endpoint POST /api/gateway/sync
 * @header Authorization: Bearer <apiKey>
 * @body {
 *   labels: Array<{
 *     serialNumber: string,
 *     batteryPercent?: number,
 *     status: "online" | "offline" | "error" | "updating",
 *     lastError?: string,
 *     displayWidth?: number,
 *     displayHeight?: number
 *   }>,
 *   firmwareVersion?: string,
 *   ipAddress?: string
 * }
 *
 * @returns {
 *   success: boolean,
 *   pendingLabels: Array<{ serialNumber: string, productData: object }>,
 *   labelsToUpdate: Array<{ serialNumber: string, productData: object }>
 * }
 *
 * @example
 * // Gateway syncing its labels
 * POST /api/gateway/sync
 * Authorization: Bearer gw_abc123...
 * Content-Type: application/json
 *
 * {
 *   "labels": [
 *     { "serialNumber": "LBL-001", "status": "online", "batteryPercent": 85 }
 *   ],
 *   "firmwareVersion": "1.0.0",
 *   "ipAddress": "192.168.1.100"
 * }
 *
 * // Response with instructions for gateway:
 * {
 *   "success": true,
 *   "pendingLabels": [
 *     { "serialNumber": "LBL-002", "productData": {...} }
 *   ],
 *   "labelsToUpdate": [
 *     { "serialNumber": "LBL-001", "productData": {...} }
 *   ]
 * }
 */
export async function POST(request: NextRequest) {
  try {
    // Extract and validate API key
    const apiKey = extractApiKey(request);
    if (!apiKey) {
      logger.warn("Missing or invalid Authorization header");
      return NextResponse.json(
        { error: "Missing or invalid Authorization header" },
        { status: 401 },
      );
    }

    logger.info(`Sync request with API key: ${apiKey.substring(0, 10)}...`);

    // Parse and validate request body
    const body = await request.json();
    const validation = gatewaySyncValidator.safeParse(body);

    if (!validation.success) {
      logger.warn(`Invalid request body: ${jts(validation.error.flatten())}`);
      return NextResponse.json(
        { error: "Invalid request body", details: validation.error.flatten() },
        { status: 400 },
      );
    }

    // Process sync request
    const result = await gatewayService.sync({
      apiKey,
      data: validation.data,
    });

    logger.debug(`Sync completed for gateway`);
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof Error && error.message === "Invalid API key.") {
      logger.warn("Invalid API key");
      return NextResponse.json({ error: "Invalid API key" }, { status: 401 });
    }

    logger.error(`Error processing sync: ${error}`);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}

/**
 * Gateway Acknowledgment API
 *
 * This endpoint is used by gateway devices to acknowledge label updates.
 * After attempting to update labels, the gateway reports success/failure.
 *
 * @endpoint PUT /api/gateway/sync
 * @header Authorization: Bearer <apiKey>
 * @body {
 *   results: Array<{
 *     labelSerialNumber: string,
 *     success: boolean,
 *     error?: string
 *   }>
 * }
 *
 * @returns { success: boolean }
 *
 * @example
 * // Gateway acknowledging label updates
 * PUT /api/gateway/sync
 * Authorization: Bearer gw_abc123...
 * Content-Type: application/json
 *
 * {
 *   "results": [
 *     { "labelSerialNumber": "LBL-001", "success": true },
 *     { "labelSerialNumber": "LBL-002", "success": false, "error": "Connection lost" }
 *   ]
 * }
 */
export async function PUT(request: NextRequest) {
  try {
    // Extract and validate API key
    const apiKey = extractApiKey(request);
    if (!apiKey) {
      logger.warn("Missing or invalid Authorization header");
      return NextResponse.json(
        { error: "Missing or invalid Authorization header" },
        { status: 401 },
      );
    }

    // Parse and validate request body
    const body = await request.json();
    const validation = gatewayAckValidator.safeParse(body);

    if (!validation.success) {
      logger.warn(`Invalid request body: ${jts(validation.error.flatten())}`);
      return NextResponse.json(
        { error: "Invalid request body", details: validation.error.flatten() },
        { status: 400 },
      );
    }

    // Process acknowledgment
    const result = await gatewayService.acknowledge({
      apiKey,
      data: validation.data,
    });

    logger.debug(`Acknowledgment processed for gateway`);
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof Error && error.message === "Invalid API key.") {
      logger.warn("Invalid API key");
      return NextResponse.json({ error: "Invalid API key" }, { status: 401 });
    }

    logger.error(`Error processing acknowledgment: ${error}`);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
