"use client";

import { authClient } from "@/lib/better-auth/client";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function SignOutPage() {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  useEffect(() => {
    const handleSignOut = async () => {
      try {
        setPending(true);
        await authClient.signOut({
          fetchOptions: {
            onSuccess: () => {
              router.push("/sign-in");
              router.refresh();
            },
          },
        });
      } catch (error) {
        console.error("Error signing out:", error);
      } finally {
        setPending(false);
      }
    };
    void handleSignOut();
  }, [router]);

  return (
    <div className="bg-background flex min-h-screen w-full items-center justify-center">
      <Loader2 size={16} className="text-muted-foreground mr-2 animate-spin" />
      <p className="text-muted-foreground text-sm">Signing you out...</p>
    </div>
  );
}
