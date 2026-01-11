ALTER TABLE "subscription" ALTER COLUMN "status" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "subscription" ALTER COLUMN "cancel_at_period_end" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "subscription" ALTER COLUMN "created_at" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "subscription" ALTER COLUMN "updated_at" DROP DEFAULT;