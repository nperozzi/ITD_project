import { stripe } from "@better-auth/stripe";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";

import Stripe from "stripe";

import { db } from "@/database";
import { env } from "@/env";

const stripeClient = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2025-12-15.clover",
});

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg", // or "pg" or "mysql"
  }),
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: {
    // github: {
    //   clientId: env.BETTER_AUTH_GITHUB_CLIENT_ID,
    //   clientSecret: env.BETTER_AUTH_GITHUB_CLIENT_SECRET,
    //   redirectURI: "http://localhost:3000/api/auth/callback/github",
    // },
  },
  plugins: [
    stripe({
      stripeClient,
      stripeWebhookSecret: env.STRIPE_WEBHOOK_SECRET,
      createCustomerOnSignUp: true,
      subscription: {
        enabled: true,
        plans: [
          {
            name: "basic", // the name of the plan, it'll be automatically lower cased when stored in the database
            priceId: "price_1SoAHqKBiO9LIq9bprI8aXZP", // TODO: Replace with your actual Stripe Price ID
            limits: {},
          },
        ],
      },
    }),
  ],
});

export type Session = typeof auth.$Infer.Session;
