import { Button } from "@/components/ui/button";
import { auth } from "@/lib/better-auth";
import { headers } from "next/headers";
import Link from "next/link";

export default async function IndexPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    return (
      <main className="flex h-screen w-screen flex-col items-center justify-center gap-2">
        <div>Please sign in to continue.</div>
        <Link href="/sign-in">
          <Button>Sign In</Button>
        </Link>
      </main>
    );
  }

  const plan = await auth.api.listActiveSubscriptions({
    headers: await headers(),
  });
  const username = session?.user.name || "Guest";
  return (
    <main className="flex h-screen w-screen flex-col items-center justify-center gap-2">
      <div>
        Hello, {username}! Your plan is{" "}
        {plan[0] &&
          (plan[0]?.plan.substring(0, 1).toUpperCase() +
            plan[0]?.plan.substring(1) ||
            "Free")}
        .
      </div>
      <Link href="/sign-out">
        <Button>Sign Out</Button>
      </Link>
      <Link href="/settings">
        <Button>Go to Settings</Button>
      </Link>
    </main>
  );
}
