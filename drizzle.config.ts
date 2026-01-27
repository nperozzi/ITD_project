import { type Config } from "drizzle-kit";

import { env } from "@/env";

export default {
  schema: "./src/database/schema.ts",
  dialect: "turso",
  dbCredentials: {
    url: env.TURSO_CONNECTION_URL,
    authToken: env.TURSO_AUTH_TOKEN,
  },
} satisfies Config;
