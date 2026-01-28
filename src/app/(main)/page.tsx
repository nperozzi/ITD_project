import DashboardView from "@/app/(main)/_components/dashboard/dashboard-view";
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

  const username = session?.user.name || "Guest";
  return <DashboardView username={username} />;
}
