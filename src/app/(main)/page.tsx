import { auth } from "@/lib/better-auth";
import { headers } from "next/headers";
import { DashboardContent } from "./_components/dashboard-content";

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  return <DashboardContent userName={session?.user.name || "User"} />;
}
