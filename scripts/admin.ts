#!/usr/bin/env bun
/**
 * ESL Admin CLI
 *
 * Command-line tool for managing gateway and label serial numbers.
 * Serial numbers are auto-generated UUIDs that act like redeemable gift cards.
 *
 * Usage:
 *   bun scripts/admin.ts <command> [options]
 *
 * Commands:
 *   gateway:create [count] [--notes <notes>]  - Create gateway serial(s) (default: 1)
 *   gateway:list                              - List all gateway serials
 *   label:create [count] [--notes <notes>]    - Create label serial(s) (default: 1)
 *   label:list                                - List all label serials
 *   help                                      - Show this help message
 *
 * Examples:
 *   bun scripts/admin.ts gateway:create                    - Create 1 gateway serial
 *   bun scripts/admin.ts gateway:create 10                 - Create 10 gateway serials
 *   bun scripts/admin.ts gateway:create 5 --notes "Batch A" - Create 5 with notes
 *   bun scripts/admin.ts gateway:list
 *   bun scripts/admin.ts label:create 50 --notes "2.9 inch display"
 *   bun scripts/admin.ts label:list
 */

import { createClient } from "@libsql/client";
import { drizzle } from "drizzle-orm/libsql";
import { gatewaySerial, labelSerial } from "../src/database/schema";

// ============================================================================
// Database Connection
// ============================================================================

const client = createClient({
  url: process.env.TURSO_CONNECTION_URL!,
  authToken: process.env.TURSO_AUTH_TOKEN,
});

const db = drizzle(client, {
  schema: { gatewaySerial, labelSerial },
});

// ============================================================================
// CLI Colors & Formatting
// ============================================================================

const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  cyan: "\x1b[36m",
};

function success(msg: string) {
  console.log(`${colors.green}✓${colors.reset} ${msg}`);
}

function error(msg: string) {
  console.error(`${colors.red}✗${colors.reset} ${msg}`);
}

function info(msg: string) {
  console.log(`${colors.blue}ℹ${colors.reset} ${msg}`);
}

function header(msg: string) {
  console.log(`\n${colors.bright}${colors.cyan}${msg}${colors.reset}\n`);
}

// ============================================================================
// Gateway Commands
// ============================================================================

async function createGatewaySerial(count: number = 1, notes?: string) {
  header(`Creating ${count} gateway serial${count > 1 ? "s" : ""}`);

  const created: string[] = [];

  for (let i = 0; i < count; i++) {
    const serialNumber = crypto.randomUUID();

    // Create serial
    const result = await db
      .insert(gatewaySerial)
      .values({
        id: crypto.randomUUID(),
        serialNumber,
        notes,
        isClaimed: false,
        createdAt: new Date(),
      })
      .returning();

    created.push(serialNumber);
    success(`Gateway serial ${i + 1}/${count}: ${serialNumber}`);
  }

  if (notes) {
    info(`Notes: ${notes}`);
  }
  info(`\nTotal created: ${created.length}`);
}

async function listGatewaySerials() {
  const serials = await db.query.gatewaySerial.findMany({
    orderBy: (serial, { desc }) => [desc(serial.createdAt)],
  });

  header("Gateway Serial Numbers");

  if (serials.length === 0) {
    info("No gateway serials found");
    return;
  }

  console.log(
    "┌──────────────────────────────────────┬──────────┬─────────────────────┬──────────────────────────────────────┐",
  );
  console.log(
    "│ Serial Number (UUID)                 │ Claimed  │ Created             │ Notes                                │",
  );
  console.log(
    "├──────────────────────────────────────┼──────────┼─────────────────────┼──────────────────────────────────────┤",
  );

  for (const serial of serials) {
    const sn = serial.serialNumber.padEnd(36);
    const claimed = serial.isClaimed
      ? `${colors.green}Yes${colors.reset}`.padEnd(17)
      : `${colors.yellow}No${colors.reset}`.padEnd(18);
    const created = serial.createdAt
      .toISOString()
      .slice(0, 19)
      .replace("T", " ");
    const notes = (serial.notes || "-").slice(0, 36).padEnd(36);
    console.log(`│ ${sn} │ ${claimed} │ ${created} │ ${notes} │`);
  }

  console.log(
    "└──────────────────────────────────────┴──────────┴─────────────────────┴──────────────────────────────────────┘",
  );

  const claimed = serials.filter((s) => s.isClaimed).length;
  info(
    `Total: ${serials.length} serials (${claimed} claimed, ${serials.length - claimed} available)`,
  );
}

// ============================================================================
// Label Commands
// ============================================================================

async function createLabelSerial(count: number = 1, notes?: string) {
  header(`Creating ${count} label serial${count > 1 ? "s" : ""}`);

  const created: string[] = [];

  for (let i = 0; i < count; i++) {
    const serialNumber = crypto.randomUUID();

    // Create serial
    const result = await db
      .insert(labelSerial)
      .values({
        id: crypto.randomUUID(),
        serialNumber,
        notes,
        isClaimed: false,
        createdAt: new Date(),
      })
      .returning();

    created.push(serialNumber);
    success(`Label serial ${i + 1}/${count}: ${serialNumber}`);
  }

  if (notes) {
    info(`Notes: ${notes}`);
  }
  info(`\nTotal created: ${created.length}`);
}

async function listLabelSerials() {
  const serials = await db.query.labelSerial.findMany({
    orderBy: (serial, { desc }) => [desc(serial.createdAt)],
  });

  header("Label Serial Numbers");

  if (serials.length === 0) {
    info("No label serials found");
    return;
  }

  console.log(
    "┌──────────────────────────────────────┬──────────┬─────────────────────┬──────────────────────────────────────┐",
  );
  console.log(
    "│ Serial Number (UUID)                 │ Claimed  │ Created             │ Notes                                │",
  );
  console.log(
    "├──────────────────────────────────────┼──────────┼─────────────────────┼──────────────────────────────────────┤",
  );

  for (const serial of serials) {
    const sn = serial.serialNumber.padEnd(36);
    const claimed = serial.isClaimed
      ? `${colors.green}Yes${colors.reset}`.padEnd(17)
      : `${colors.yellow}No${colors.reset}`.padEnd(18);
    const created = serial.createdAt
      .toISOString()
      .slice(0, 19)
      .replace("T", " ");
    const notes = (serial.notes || "-").slice(0, 36).padEnd(36);
    console.log(`│ ${sn} │ ${claimed} │ ${created} │ ${notes} │`);
  }

  console.log(
    "└──────────────────────────────────────┴──────────┴─────────────────────┴──────────────────────────────────────┘",
  );

  const claimed = serials.filter((s) => s.isClaimed).length;
  info(
    `Total: ${serials.length} serials (${claimed} claimed, ${serials.length - claimed} available)`,
  );
}

// ============================================================================
// Help Command
// ============================================================================

function showHelp() {
  console.log(`
${colors.bright}${colors.cyan}ESL Admin CLI${colors.reset}

Command-line tool for managing gateway and label serial numbers.
Serial numbers are auto-generated UUIDs.

${colors.bright}Usage:${colors.reset}
  bun scripts/admin.ts <command> [options]

${colors.bright}Commands:${colors.reset}
  ${colors.yellow}gateway:create${colors.reset} [count] [--notes <notes>]
    Create gateway serial number(s) (default count: 1)

  ${colors.yellow}gateway:list${colors.reset}
    List all gateway serial numbers

  ${colors.yellow}label:create${colors.reset} [count] [--notes <notes>]
    Create label serial number(s) (default count: 1)

  ${colors.yellow}label:list${colors.reset}
    List all label serial numbers

  ${colors.yellow}help${colors.reset}
    Show this help message

${colors.bright}Examples:${colors.reset}
  bun scripts/admin.ts gateway:create                    - Create 1 gateway
  bun scripts/admin.ts gateway:create 10                 - Create 10 gateways
  bun scripts/admin.ts gateway:create 5 --notes "Batch A"
  bun scripts/admin.ts gateway:list
  bun scripts/admin.ts label:create 50 --notes "2.9 inch display"
  bun scripts/admin.ts label:list

${colors.bright}Serial Numbers:${colors.reset}
  - Auto-generated UUIDs (e.g., 550e8400-e29b-41d4-a716-446655440000)
  - Guaranteed unique
  - No format restrictions or collisions

${colors.bright}Environment Variables:${colors.reset}
  TURSO_CONNECTION_URL  - Database connection URL (required)
  TURSO_AUTH_TOKEN      - Database auth token (optional for local)
`);
}

// ============================================================================
// CLI Parser
// ============================================================================

function parseArgs(args: string[]): {
  command: string;
  positional: string[];
  flags: Record<string, string>;
} {
  const command = args[0] || "help";
  const positional: string[] = [];
  const flags: Record<string, string> = {};

  for (let i = 1; i < args.length; i++) {
    if (args[i]?.startsWith("--")) {
      const key = args[i]!.slice(2);
      const value = args[++i] || "";
      flags[key] = value;
    } else if (args[i]) {
      positional.push(args[i]!);
    }
  }

  return { command, positional, flags };
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  const args = process.argv.slice(2);
  const { command, positional, flags } = parseArgs(args);

  try {
    switch (command) {
      case "gateway:create": {
        const count = parseInt(positional[0] || "1", 10);
        if (count <= 0) {
          error("Count must be a positive number");
          console.log(
            "Usage: bun scripts/admin.ts gateway:create [count] [--notes <notes>]",
          );
          process.exit(1);
        }
        await createGatewaySerial(count, flags.notes);
        break;
      }

      case "gateway:list":
        await listGatewaySerials();
        break;

      case "label:create": {
        const count = parseInt(positional[0] || "1", 10);
        if (count <= 0) {
          error("Count must be a positive number");
          console.log(
            "Usage: bun scripts/admin.ts label:create [count] [--notes <notes>]",
          );
          process.exit(1);
        }
        await createLabelSerial(count, flags.notes);
        break;
      }

      case "label:list":
        await listLabelSerials();
        break;

      case "help":
      default:
        showHelp();
        break;
    }
  } catch (err) {
    error(`Command failed: ${err}`);
    process.exit(1);
  }
}

main();
