"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/trpc/react";
import {
  AlertCircle,
  Battery,
  Package,
  Plus,
  Router,
  Tag,
  Wifi,
  WifiOff,
} from "lucide-react";
import Link from "next/link";

interface DashboardContentProps {
  userName: string;
}

export function DashboardContent({ userName }: DashboardContentProps) {
  const { data: gateways, isLoading: gatewaysLoading } =
    api.gateway.readAll.useQuery(undefined, {
      refetchInterval: 5000, // Auto-refresh every 5 seconds
    });
  const { data: labels, isLoading: labelsLoading } =
    api.gateway.readAllLabels.useQuery(undefined, {
      refetchInterval: 5000, // Auto-refresh every 5 seconds
    });
  const { data: products, isLoading: productsLoading } =
    api.product.readAll.useQuery(undefined, {
      refetchInterval: 5000, // Auto-refresh every 5 seconds
    });

  const onlineGateways = gateways?.filter((g) => g.isOnline).length || 0;
  const onlineLabels = labels?.filter((l) => l.status === "online").length || 0;
  const pendingLabels =
    labels?.filter((l) => l.status === "pending").length || 0;
  const errorLabels = labels?.filter((l) => l.status === "error").length || 0;

  return (
    <div className="space-y-6 p-6">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome back, {userName}
        </h1>
        <p className="text-muted-foreground">
          Here's an overview of your electronic shelf label system.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Gateways
            </CardTitle>
            <Router className="text-muted-foreground h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {gatewaysLoading ? "..." : gateways?.length || 0}
            </div>
            <p className="text-muted-foreground text-xs">
              <span className="text-green-500">{onlineGateways} online</span>
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Labels</CardTitle>
            <Tag className="text-muted-foreground h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {labelsLoading ? "..." : labels?.length || 0}
            </div>
            <p className="text-muted-foreground text-xs">
              <span className="text-green-500">{onlineLabels} online</span>
              {pendingLabels > 0 && (
                <span className="ml-2 text-yellow-500">
                  {pendingLabels} pending
                </span>
              )}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Products</CardTitle>
            <Package className="text-muted-foreground h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {productsLoading ? "..." : products?.length || 0}
            </div>
            <p className="text-muted-foreground text-xs">In your catalog</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alerts</CardTitle>
            <AlertCircle className="text-muted-foreground h-4 w-4" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {labelsLoading ? "..." : errorLabels}
            </div>
            <p className="text-muted-foreground text-xs">
              {errorLabels > 0 ? (
                <span className="text-red-500">Labels need attention</span>
              ) : (
                <span className="text-green-500">All systems normal</span>
              )}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Router className="h-5 w-5" />
              Gateways
            </CardTitle>
            <CardDescription>
              Manage your gateway devices that connect labels to the network.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/gateways">
              <Button className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Add Gateway
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Tag className="h-5 w-5" />
              Labels
            </CardTitle>
            <CardDescription>
              Register and manage your electronic shelf labels.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/labels">
              <Button className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Add Label
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Products
            </CardTitle>
            <CardDescription>
              Create products with pricing to display on your labels.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/products">
              <Button className="w-full">
                <Plus className="mr-2 h-4 w-4" />
                Add Product
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity / Device Status */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Gateway Status */}
        <Card>
          <CardHeader>
            <CardTitle>Gateway Status</CardTitle>
            <CardDescription>
              Real-time status of your gateway devices
            </CardDescription>
          </CardHeader>
          <CardContent>
            {gatewaysLoading ? (
              <div className="text-muted-foreground">Loading...</div>
            ) : gateways && gateways.length > 0 ? (
              <div className="space-y-4">
                {gateways.slice(0, 5).map((gateway) => (
                  <div
                    key={gateway.id}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      {gateway.isOnline ? (
                        <Wifi className="h-4 w-4 text-green-500" />
                      ) : (
                        <WifiOff className="text-muted-foreground h-4 w-4" />
                      )}
                      <div>
                        <p className="font-medium">{gateway.name}</p>
                        <p className="text-muted-foreground text-xs">
                          {gateway.serialNumber}
                        </p>
                      </div>
                    </div>
                    <Badge variant={gateway.isOnline ? "default" : "secondary"}>
                      {gateway.isOnline ? "Online" : "Offline"}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center">
                <Router className="text-muted-foreground mx-auto mb-2 h-12 w-12" />
                <p className="text-muted-foreground">No gateways registered</p>
                <Link href="/gateways">
                  <Button variant="link" className="mt-2">
                    Add your first gateway
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Label Status */}
        <Card>
          <CardHeader>
            <CardTitle>Label Status</CardTitle>
            <CardDescription>
              Overview of your electronic shelf labels
            </CardDescription>
          </CardHeader>
          <CardContent>
            {labelsLoading ? (
              <div className="text-muted-foreground">Loading...</div>
            ) : labels && labels.length > 0 ? (
              <div className="space-y-4">
                {labels.slice(0, 5).map((label) => (
                  <div
                    key={label.id}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1">
                        {label.batteryPercent !== null && (
                          <Battery
                            className={`h-4 w-4 ${
                              label.batteryPercent > 20
                                ? "text-green-500"
                                : "text-red-500"
                            }`}
                          />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{label.name}</p>
                        <p className="text-muted-foreground text-xs">
                          {label.product?.name || "No product assigned"}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={
                        label.status === "online"
                          ? "default"
                          : label.status === "pending"
                            ? "outline"
                            : label.status === "error"
                              ? "destructive"
                              : "secondary"
                      }
                    >
                      {label.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center">
                <Tag className="text-muted-foreground mx-auto mb-2 h-12 w-12" />
                <p className="text-muted-foreground">No labels registered</p>
                <Link href="/labels">
                  <Button variant="link" className="mt-2">
                    Add your first label
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
