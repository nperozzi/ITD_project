import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { checkGatewayClaimValidator } from "@/services/gateway/gateway.input";
import { gatewayService } from "@/services/gateway/gateway.service";
import { NextRequest, NextResponse } from "next/server";

const logger = new Logger("GatewayClaimAPI");

/**
 * Gateway Claim Status API
 *
 * This endpoint is used by gateway devices to check if they have been claimed.
 * The gateway device should poll this endpoint periodically.
 *
 * @endpoint GET /api/gateway/claim
 * @query serialNumber - The serial number of the gateway device
 *
 * @returns
 * - 200: { status: "unclaimed" } - Gateway is valid but not yet claimed
 * - 200: { status: "claimed", apiKey: string, gatewayId: string, name: string, ownerId: string } - Gateway is claimed
 * - 200: { status: "invalid", message: string } - Serial number not found in system
 * - 400: { error: string } - Invalid request (missing serial number)
 * - 500: { error: string } - Server error
 *
 * @example
 * // Gateway polling for claim status
 * GET /api/gateway/claim?serialNumber=89de18d6-d7af-471b-9858-f3a22f3db368
 *
 * // Response when unclaimed:
 * { "status": "unclaimed" }
 *
 * // Response when claimed:
 * { "status": "claimed", "apiKey": "gw_abc123...", "gatewayId": "...", "name": "My Gateway", "ownerId": "..." }
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const serialNumber = searchParams.get("serialNumber");

    // Validate input
    const validation = checkGatewayClaimValidator.safeParse({ serialNumber });
    if (!validation.success) {
      logger.warn(`Invalid request: ${jts(validation.error.flatten())}`);
      return NextResponse.json(
        { error: "Serial number is required" },
        { status: 400 },
      );
    }

    // Check claim status
    const status = await gatewayService.checkSerialStatus({
      serialNumber: validation.data.serialNumber.toLowerCase(),
    });

    if (!status.valid) {
      logger.warn(`Unknown serial number: ${serialNumber}`);
      return NextResponse.json({
        status: "invalid",
        message: "Serial number not registered in the system",
      });
    }

    if (status.claimed && status.gateway) {
      logger.debug(`Gateway ${serialNumber} is claimed`);

      // Gateway info is already included in status from checkSerialStatus
      return NextResponse.json({
        status: "claimed",
        apiKey: status.gateway.apiKey,
        gatewayId: status.gateway.id,
        name: status.gateway.name ?? "Unnamed Gateway",
        ownerId: status.gateway.ownerId,
      });
    }

    logger.debug(`Gateway ${serialNumber} is not claimed`);
    return NextResponse.json({ status: "unclaimed" });
  } catch (error) {
    logger.error(`Error checking claim status: ${error}`);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
