"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { authClient } from "@/lib/better-auth/client";
import { Check, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function SettingsPage() {
  const router = useRouter();
  const { data: session, isPending: isSessionLoading } =
    authClient.useSession();
  const [activeSubscription, setActiveSubscription] = useState<any>(null);
  const [isLoadingSubscription, setIsLoadingSubscription] = useState(true);
  const [isBillingLoading, setIsBillingLoading] = useState(false);
  const [isUpgrading, setIsUpgrading] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSubscription() {
      try {
        const { data } = await authClient.subscription.list();
        if (data && data.length > 0) {
          // Assuming user has one active subscription for simplicity
          setActiveSubscription(data[0]);
        }
      } catch (error) {
        console.error("Failed to fetch subscription", error);
      } finally {
        setIsLoadingSubscription(false);
      }
    }

    if (session) {
      fetchSubscription();
    } else if (!isSessionLoading) {
      setIsLoadingSubscription(false);
    }
  }, [session, isSessionLoading]);

  const handleBillingPortal = async () => {
    setIsBillingLoading(true);
    try {
      const { data, error } = await authClient.subscription.billingPortal({
        returnUrl: window.location.href,
      });
      if (data?.url) {
        window.location.href = data.url;
      }
      if (error) {
        console.error("Billing portal error:", error);
      }
    } catch (error) {
      console.error("Billing portal exception:", error);
    } finally {
      setIsBillingLoading(false);
    }
  };

  const handleUpgrade = async (priceId: string, planName: string) => {
    setIsUpgrading(priceId);
    try {
      const { data, error } = await authClient.subscription.upgrade({
        plan: planName,
        successUrl: window.location.href,
        cancelUrl: window.location.href,
      });
      if (data?.url) {
        window.location.href = data.url;
      }
      if (error) {
        console.error("Upgrade error:", error);
      }
    } catch (error) {
      console.error("Upgrade exception:", error);
    } finally {
      setIsUpgrading(null);
    }
  };

  if (isSessionLoading || isLoadingSubscription) {
    return (
      <div className="container mx-auto max-w-4xl space-y-8 px-4 py-10">
        <Skeleton className="h-12 w-48" />
        <div className="grid gap-6">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      </div>
    );
  }

  if (!session) {
    // Ideally redirect or show login
    return (
      <div className="container mx-auto px-4 py-10 text-center">
        <h1 className="mb-4 text-2xl font-bold">Access Denied</h1>
        <p className="mb-8">You need to be signed in to view settings.</p>
        <Button onClick={() => router.push("/sign-in")}>Sign In</Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-4xl space-y-8 px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      </div>

      {/* Profile Section */}
      <Card>
        <CardHeader>
          <CardTitle>Profile</CardTitle>
          <CardDescription>Manage your account information.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <span className="text-muted-foreground text-sm font-medium">
                Name
              </span>
              <p className="font-medium">{session.user.name}</p>
            </div>
            <div className="space-y-2">
              <span className="text-muted-foreground text-sm font-medium">
                Email
              </span>
              <p className="font-medium">{session.user.email}</p>
            </div>
            <div className="space-y-2">
              <span className="text-muted-foreground text-sm font-medium">
                User ID
              </span>
              <p className="text-muted-foreground font-mono text-sm">
                {session.user.id}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Subscription Section */}
      <Card>
        <CardHeader>
          <CardTitle>Subscription</CardTitle>
          <CardDescription>Manage your plan and billing.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {activeSubscription ? (
            <div className="bg-muted/50 rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-semibold capitalize">
                      {activeSubscription.plan} Plan
                    </h3>
                    <Badge
                      variant={
                        activeSubscription.status === "active"
                          ? "default"
                          : "secondary"
                      }
                    >
                      {activeSubscription.status}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground text-sm">
                    {activeSubscription.cancelAtPeriodEnd
                      ? `Cancels on ${new Date(activeSubscription.periodEnd).toLocaleDateString()}`
                      : `Renews on ${new Date(activeSubscription.periodEnd).toLocaleDateString()}`}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-muted/20 rounded-lg border p-8 text-center">
              <p className="text-muted-foreground">
                You are currently on the free plan.
              </p>
            </div>
          )}

          {activeSubscription && (
            <Button
              variant="outline"
              onClick={handleBillingPortal}
              disabled={isBillingLoading}
            >
              {isBillingLoading && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Manage Billing
            </Button>
          )}

          {/* Available Plans */}
          {!activeSubscription && (
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              {/* Basic Plan */}
              <Card className="relative flex flex-col">
                <CardHeader>
                  <CardTitle>Basic</CardTitle>
                  <CardDescription>
                    Essential features for getting started.
                  </CardDescription>
                  <div className="mt-4">
                    <span className="text-3xl font-bold">$10</span>
                    <span className="text-muted-foreground">/month</span>
                  </div>
                </CardHeader>
                <CardContent className="flex-1">
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <Check className="text-primary h-4 w-4" />
                      <span>Basic Features</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="text-primary h-4 w-4" />
                      <span>Community Support</span>
                    </li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button
                    className="w-full"
                    onClick={() =>
                      handleUpgrade("price_1SoAHqKBiO9LIq9bprI8aXZP", "basic")
                    }
                    disabled={!!isUpgrading}
                  >
                    {isUpgrading === "price_1SoAHqKBiO9LIq9bprI8aXZP" && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Subscribe to Basic
                  </Button>
                </CardFooter>
              </Card>

              {/* Example Pro Plan (Mock) */}
              <Card className="border-primary relative flex flex-col shadow-sm">
                <div className="bg-primary text-primary-foreground absolute -top-3 right-0 left-0 mx-auto w-fit rounded-full px-3 py-1 text-xs">
                  Popular
                </div>
                <CardHeader>
                  <CardTitle>Pro</CardTitle>
                  <CardDescription>
                    Advanced features for power users.
                  </CardDescription>
                  <div className="mt-4">
                    <span className="text-3xl font-bold">$29</span>
                    <span className="text-muted-foreground">/month</span>
                  </div>
                </CardHeader>
                <CardContent className="flex-1">
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <Check className="text-primary h-4 w-4" />
                      <span>Everything in Basic</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="text-primary h-4 w-4" />
                      <span>Priority Support</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="text-primary h-4 w-4" />
                      <span>Advanced Analytics</span>
                    </li>
                  </ul>
                </CardContent>
                <CardFooter>
                  <Button
                    className="w-full"
                    variant="default"
                    // Note: This needs a real priceID in config to work
                    onClick={() =>
                      alert(
                        "Configure Pro plan price ID in src/lib/better-auth/config.ts",
                      )
                    }
                  >
                    Subscribe to Pro
                  </Button>
                </CardFooter>
              </Card>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
