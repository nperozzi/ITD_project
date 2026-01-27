import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const subscription = sqliteTable("subscription", {
  id: text("id").primaryKey(),
  plan: text("plan").notNull(),
  referenceId: text("reference_id").notNull(),
  stripeCustomerId: text("stripe_customer_id"),
  stripeSubscriptionId: text("stripe_subscription_id"),
  status: text("status"),
  periodStart: integer("period_start", { mode: "timestamp" }),
  periodEnd: integer("period_end", { mode: "timestamp" }),
  cancelAtPeriodEnd: integer("cancel_at_period_end", { mode: "boolean" }),
  cancelAt: integer("cancel_at", { mode: "timestamp" }),
  canceledAt: integer("canceled_at", { mode: "timestamp" }),
  endedAt: integer("ended_at", { mode: "timestamp" }),
  trialStart: integer("trial_start", { mode: "timestamp" }),
  trialEnd: integer("trial_end", { mode: "timestamp" }),
  seats: integer("seats"),
  createdAt: integer("created_at", { mode: "timestamp" })
    .$defaultFn(() => new Date())
    .notNull(),
  updatedAt: integer("updated_at", { mode: "timestamp" })
    .$defaultFn(() => new Date())
    .notNull(),
});
