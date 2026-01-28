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
 * - 200: { claimed: false } - Gateway is valid but not yet claimed
 * - 200: { claimed: true, apiKey: string } - Gateway is claimed, use apiKey for sync
 * - 400: { error: string } - Invalid request (missing serial number)
 * - 404: { error: string } - Serial number not found in system
 * - 500: { error: string } - Server error
 *
 * @example
 * // Gateway polling for claim status
 * GET /api/gateway/claim?serialNumber=GW-ABCD-1234
 *
 * // Response when unclaimed:
 * { "claimed": false }
 *
 * // Response when claimed:
 * { "claimed": true, "apiKey": "gw_abc123..." }
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
      serialNumber: validation.data.serialNumber,
    });

    if (!status.valid) {
      logger.warn(`Unknown serial number: ${serialNumber}`);
      return NextResponse.json(
        { error: "Serial number not found" },
        { status: 404 },
      );
    }

    if (status.claimed && status.gateway) {
      logger.debug(`Gateway ${serialNumber} is claimed`);
      return NextResponse.json({
        claimed: true,
        apiKey: status.gateway.apiKey,
      });
    }

    logger.debug(`Gateway ${serialNumber} is not claimed`);
    return NextResponse.json({ claimed: false });
  } catch (error) {
    logger.error(`Error checking claim status: ${error}`);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
