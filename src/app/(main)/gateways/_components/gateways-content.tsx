"use client";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/trpc/react";
import {
  Check,
  Copy,
  MoreHorizontal,
  Pencil,
  Plus,
  Router,
  Trash2,
  Wifi,
  WifiOff,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export function GatewaysContent() {
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [serialNumber, setSerialNumber] = useState("");
  const [gatewayName, setGatewayName] = useState("");
  const [editingGateway, setEditingGateway] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const utils = api.useUtils();
  const { data: gateways, isLoading } = api.gateway.readAll.useQuery(
    undefined,
    {
      refetchInterval: 5000, // Auto-refresh every 5 seconds
    },
  );

  const claimMutation = api.gateway.claim.useMutation({
    onSuccess: () => {
      toast.success("Gateway registered successfully!");
      setIsAddOpen(false);
      setSerialNumber("");
      setGatewayName("");
      utils.gateway.readAll.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const updateMutation = api.gateway.update.useMutation({
    onSuccess: () => {
      toast.success("Gateway updated successfully!");
      setIsEditOpen(false);
      setEditingGateway(null);
      utils.gateway.readAll.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const deleteMutation = api.gateway.delete.useMutation({
    onSuccess: () => {
      toast.success("Gateway deleted successfully!");
      utils.gateway.readAll.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleClaim = () => {
    if (!serialNumber.trim() || !gatewayName.trim()) {
      toast.error("Please fill in all fields");
      return;
    }
    claimMutation.mutate({
      serialNumber: serialNumber.toUpperCase().trim(),
      name: gatewayName.trim(),
    });
  };

  const handleUpdate = () => {
    if (!editingGateway || !editingGateway.name.trim()) {
      toast.error("Please enter a name");
      return;
    }
    updateMutation.mutate({
      id: editingGateway.id,
      name: editingGateway.name.trim(),
    });
  };

  const handleCopySerial = async (serial: string, id: string) => {
    await navigator.clipboard.writeText(serial);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
    toast.success("Serial number copied!");
  };

  const formatDate = (date: Date | null) => {
    if (!date) return "Never";
    return new Date(date).toLocaleString();
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gateways</h1>
          <p className="text-muted-foreground">
            Manage your gateway devices that connect labels to the network.
          </p>
        </div>
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Gateway
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Register a Gateway</DialogTitle>
              <DialogDescription>
                Enter the serial number printed on your gateway device to
                register it. This will claim the gateway and allow it to connect
                to your account.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="serial">Serial Number</Label>
                <Input
                  id="serial"
                  placeholder="GW-XXXX-XXXX"
                  value={serialNumber}
                  onChange={(e) =>
                    setSerialNumber(e.target.value.toUpperCase())
                  }
                />
                <p className="text-muted-foreground text-xs">
                  The serial number is printed on the bottom of your gateway
                  device.
                </p>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="name">Gateway Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., Store Front, Warehouse A"
                  value={gatewayName}
                  onChange={(e) => setGatewayName(e.target.value)}
                />
                <p className="text-muted-foreground text-xs">
                  Give your gateway a friendly name to identify it.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleClaim} disabled={claimMutation.isPending}>
                {claimMutation.isPending
                  ? "Registering..."
                  : "Register Gateway"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Gateway List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Gateways</CardTitle>
          <CardDescription>
            {gateways?.length || 0} gateway{gateways?.length !== 1 ? "s" : ""}{" "}
            registered
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-muted-foreground py-8 text-center">
              Loading gateways...
            </div>
          ) : gateways && gateways.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Status</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Serial Number</TableHead>
                  <TableHead>Last Seen</TableHead>
                  <TableHead>Firmware</TableHead>
                  <TableHead className="w-[70px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {gateways.map((gateway) => (
                  <TableRow key={gateway.id}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {gateway.isOnline ? (
                          <Wifi className="h-4 w-4 text-green-500" />
                        ) : (
                          <WifiOff className="text-muted-foreground h-4 w-4" />
                        )}
                        <Badge
                          variant={gateway.isOnline ? "default" : "secondary"}
                        >
                          {gateway.isOnline ? "Online" : "Offline"}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">
                      {gateway.name}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <code className="bg-muted rounded px-2 py-1 text-xs">
                          {gateway.serialNumber}
                        </code>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() =>
                            handleCopySerial(gateway.serialNumber, gateway.id)
                          }
                        >
                          {copiedId === gateway.id ? (
                            <Check className="h-3 w-3" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {formatDate(gateway.lastPingAt)}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {gateway.firmwareVersion || "-"}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => {
                              setEditingGateway({
                                id: gateway.id,
                                name: gateway.name,
                              });
                              setIsEditOpen(true);
                            }}
                          >
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                          </DropdownMenuItem>
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <DropdownMenuItem
                                onSelect={(e) => e.preventDefault()}
                                className="text-destructive"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                              </DropdownMenuItem>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>
                                  Delete Gateway
                                </AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to delete "
                                  {gateway.name}"? This action cannot be undone
                                  and will disconnect all labels associated with
                                  this gateway.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() =>
                                    deleteMutation.mutate({ id: gateway.id })
                                  }
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="py-12 text-center">
              <Router className="text-muted-foreground mx-auto mb-4 h-12 w-12" />
              <h3 className="mb-2 text-lg font-semibold">
                No gateways registered
              </h3>
              <p className="text-muted-foreground mb-4">
                Register your first gateway to start connecting labels.
              </p>
              <Button onClick={() => setIsAddOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Gateway
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Gateway</DialogTitle>
            <DialogDescription>
              Update the name of your gateway device.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-name">Gateway Name</Label>
              <Input
                id="edit-name"
                value={editingGateway?.name || ""}
                onChange={(e) =>
                  setEditingGateway((prev) =>
                    prev ? { ...prev, name: e.target.value } : null,
                  )
                }
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdate} disabled={updateMutation.isPending}>
              {updateMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
