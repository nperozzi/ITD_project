import { stripeClient } from "@better-auth/stripe/client";
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  plugins: [
    stripeClient({
      subscription: true,
    }),
  ],
});

export type Session = typeof authClient.$Infer.Session;
