"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authClient } from "@/lib/better-auth/client";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

export default function ForgotPassword(props: { callbackURL?: string }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const callbackURL = props.callbackURL ?? "/reset-password";

  return (
    <Card className="z-50 min-h-screen w-full rounded-none border-0 shadow-none md:h-auto md:min-h-0 md:max-w-md md:rounded-xl md:border md:shadow-sm">
      <CardHeader>
        <CardTitle className="text-lg md:text-xl">Forgot Password</CardTitle>
        <CardDescription className="text-xs md:text-sm">
          Enter your email to receive a password reset link
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              required
              onChange={(e) => {
                setEmail(e.target.value);
              }}
              value={email}
            />
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading}
            onClick={async () => {
              await authClient.requestPasswordReset(
                {
                  email,
                  redirectTo: callbackURL,
                },
                {
                  onRequest: () => {
                    setLoading(true);
                  },
                  onResponse: () => {
                    setLoading(false);
                  },
                  onSuccess: () => {
                    toast.success(
                      "If an account exists, a reset link has been sent to your email.",
                    );
                  },
                  onError: (ctx) => {
                    toast.error(ctx.error.message);
                  },
                },
              );
            }}
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <p>Send Reset Link</p>
            )}
          </Button>

          <div className="text-center text-sm">
            <Link
              href="/sign-in"
              className="flex items-center justify-center gap-2 underline"
            >
              <ArrowLeft size={16} /> Back to Sign In
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
