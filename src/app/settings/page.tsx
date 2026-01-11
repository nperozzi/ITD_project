"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/better-auth/client";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Loader2, Check } from "lucide-react";

export default function SettingsPage() {
  const router = useRouter();
  const { data: session, isPending: isSessionLoading } = authClient.useSession();
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
      <div className="container mx-auto py-10 px-4 space-y-8 max-w-4xl">
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
        <div className="container mx-auto py-10 px-4 text-center">
            <h1 className="text-2xl font-bold mb-4">Access Denied</h1>
            <p className="mb-8">You need to be signed in to view settings.</p>
            <Button onClick={() => router.push("/sign-in")}>Sign In</Button>
        </div>
     )
  }

  return (
    <div className="container mx-auto py-10 px-4 space-y-8 max-w-4xl">
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <span className="text-sm font-medium text-muted-foreground">Name</span>
              <p className="font-medium">{session.user.name}</p>
            </div>
            <div className="space-y-2">
              <span className="text-sm font-medium text-muted-foreground">Email</span>
              <p className="font-medium">{session.user.email}</p>
            </div>
            <div className="space-y-2">
               <span className="text-sm font-medium text-muted-foreground">User ID</span>
               <p className="text-sm font-mono text-muted-foreground">{session.user.id}</p>
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
            <div className="rounded-lg border p-4 bg-muted/50">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-lg capitalize">
                      {activeSubscription.plan} Plan
                    </h3>
                    <Badge variant={activeSubscription.status === "active" ? "default" : "secondary"}>
                      {activeSubscription.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {activeSubscription.cancelAtPeriodEnd 
                      ? `Cancels on ${new Date(activeSubscription.periodEnd).toLocaleDateString()}` 
                      : `Renews on ${new Date(activeSubscription.periodEnd).toLocaleDateString()}`}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="rounded-lg border p-8 text-center bg-muted/20">
              <p className="text-muted-foreground">You are currently on the free plan.</p>
            </div>
          )}

          {activeSubscription && (
             <Button 
                variant="outline" 
                onClick={handleBillingPortal} 
                disabled={isBillingLoading}
            >
                {isBillingLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Manage Billing
            </Button>
          )}

          {/* Available Plans */}
          {!activeSubscription && (
            <div className="grid md:grid-cols-2 gap-6 mt-6">
                {/* Basic Plan */}
                <Card className="relative flex flex-col">
                    <CardHeader>
                        <CardTitle>Basic</CardTitle>
                        <CardDescription>Essential features for getting started.</CardDescription>
                        <div className="mt-4">
                            <span className="text-3xl font-bold">$10</span>
                            <span className="text-muted-foreground">/month</span>
                        </div>
                    </CardHeader>
                    <CardContent className="flex-1">
                         <ul className="space-y-2 text-sm">
                            <li className="flex items-center gap-2">
                                <Check className="h-4 w-4 text-primary" />
                                <span>Basic Features</span>
                            </li>
                            <li className="flex items-center gap-2">
                                <Check className="h-4 w-4 text-primary" />
                                <span>Community Support</span>
                            </li>
                         </ul>
                    </CardContent>
                    <CardFooter>
                         <Button 
                             className="w-full" 
                             onClick={() => handleUpgrade("price_1SoAHqKBiO9LIq9bprI8aXZP", "basic")}
                             disabled={!!isUpgrading}
                        >
                            {isUpgrading === "price_1SoAHqKBiO9LIq9bprI8aXZP" && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                             Subscribe to Basic
                         </Button>
                    </CardFooter>
                </Card>

                {/* Example Pro Plan (Mock) */}
                <Card className="relative flex flex-col border-primary shadow-sm">
                     <div className="absolute -top-3 left-0 right-0 mx-auto w-fit rounded-full bg-primary px-3 py-1 text-xs text-primary-foreground">
                        Popular
                     </div>
                    <CardHeader>
                        <CardTitle>Pro</CardTitle>
                        <CardDescription>Advanced features for power users.</CardDescription>
                        <div className="mt-4">
                            <span className="text-3xl font-bold">$29</span>
                            <span className="text-muted-foreground">/month</span>
                        </div>
                    </CardHeader>
                    <CardContent className="flex-1">
                         <ul className="space-y-2 text-sm">
                            <li className="flex items-center gap-2">
                                <Check className="h-4 w-4 text-primary" />
                                <span>Everything in Basic</span>
                            </li>
                            <li className="flex items-center gap-2">
                                <Check className="h-4 w-4 text-primary" />
                                <span>Priority Support</span>
                            </li>
                            <li className="flex items-center gap-2">
                                <Check className="h-4 w-4 text-primary" />
                                <span>Advanced Analytics</span>
                            </li>
                         </ul>
                    </CardContent>
                    <CardFooter>
                         <Button 
                             className="w-full" 
                             variant="default"
                             // Note: This needs a real priceID in config to work
                             onClick={() => alert("Configure Pro plan price ID in src/lib/better-auth/config.ts")}
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
