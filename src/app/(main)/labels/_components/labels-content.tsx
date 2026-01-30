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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
  AlertCircle,
  Battery,
  Check,
  Clock,
  Loader2,
  MoreHorizontal,
  Package,
  Pencil,
  Plus,
  Radio,
  Router,
  Tag,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

type LabelStatus = "pending" | "online" | "offline" | "error" | "updating";

const statusConfig: Record<
  LabelStatus,
  {
    label: string;
    variant: "default" | "secondary" | "destructive" | "outline";
    icon: typeof Clock;
  }
> = {
  pending: { label: "Pending", variant: "outline", icon: Clock },
  online: { label: "Online", variant: "default", icon: Check },
  offline: { label: "Offline", variant: "secondary", icon: AlertCircle },
  error: { label: "Error", variant: "destructive", icon: AlertCircle },
  updating: { label: "Updating", variant: "outline", icon: Loader2 },
};

function getSignalStrength(rssi: number | null): {
  label: string;
  color: string;
  bars: number;
} {
  if (rssi === null) {
    return { label: "Unknown", color: "text-muted-foreground", bars: 0 };
  }

  // RSSI ranges (dBm):
  // Excellent: > -50
  // Good: -50 to -60
  // Fair: -60 to -70
  // Weak: -70 to -80
  // Very Weak: < -80

  if (rssi > -50) {
    return { label: "Excellent", color: "text-green-500", bars: 4 };
  } else if (rssi > -60) {
    return { label: "Good", color: "text-green-500", bars: 3 };
  } else if (rssi > -70) {
    return { label: "Fair", color: "text-yellow-500", bars: 2 };
  } else if (rssi > -80) {
    return { label: "Weak", color: "text-orange-500", bars: 1 };
  } else {
    return { label: "Very Weak", color: "text-red-500", bars: 1 };
  }
}

function SignalIndicator({ rssi }: { rssi: number | null }) {
  const signal = getSignalStrength(rssi);

  if (signal.bars === 0) {
    return (
      <div className="flex items-center gap-2">
        <Radio className="text-muted-foreground h-4 w-4" />
        <span className="text-muted-foreground text-sm">-</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-0.5">
        {[1, 2, 3, 4].map((bar) => (
          <div
            key={bar}
            className={`w-1 rounded-sm ${
              bar <= signal.bars ? signal.color : "bg-muted"
            }`}
            style={{ height: `${bar * 3 + 2}px` }}
          />
        ))}
      </div>
      <span className={`text-xs ${signal.color}`}>{rssi} dBm</span>
    </div>
  );
}

export function LabelsContent() {
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isAssignOpen, setIsAssignOpen] = useState(false);
  const [serialNumber, setSerialNumber] = useState("");
  const [labelName, setLabelName] = useState("");
  const [editingLabel, setEditingLabel] = useState<{
    id: string;
    name: string;
  } | null>(null);
  const [assigningLabel, setAssigningLabel] = useState<{
    id: string;
    name: string;
    productId: string | null;
  } | null>(null);
  const [selectedProductId, setSelectedProductId] = useState<string | null>(
    null,
  );

  const utils = api.useUtils();
  const { data: labels, isLoading } = api.gateway.readAllLabels.useQuery(
    undefined,
    {
      refetchInterval: 5000, // Auto-refresh every 5 seconds
    },
  );
  const { data: products } = api.product.readActive.useQuery();

  const registerMutation = api.gateway.registerLabel.useMutation({
    onSuccess: () => {
      toast.success("Label registered! Waiting for a gateway to find it.");
      setIsAddOpen(false);
      setSerialNumber("");
      setLabelName("");
      utils.gateway.readAllLabels.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const updateMutation = api.gateway.updateLabel.useMutation({
    onSuccess: () => {
      toast.success("Label updated successfully!");
      setIsEditOpen(false);
      setEditingLabel(null);
      utils.gateway.readAllLabels.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const assignMutation = api.gateway.assignProductToLabel.useMutation({
    onSuccess: () => {
      toast.success("Product assigned! Label will update on next sync.");
      setIsAssignOpen(false);
      setAssigningLabel(null);
      setSelectedProductId(null);
      utils.gateway.readAllLabels.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const deleteMutation = api.gateway.deleteLabel.useMutation({
    onSuccess: () => {
      toast.success("Label deleted successfully!");
      utils.gateway.readAllLabels.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleRegister = () => {
    if (!serialNumber.trim() || !labelName.trim()) {
      toast.error("Please fill in all fields");
      return;
    }
    registerMutation.mutate({
      serialNumber: serialNumber.toUpperCase().trim(),
      name: labelName.trim(),
    });
  };

  const handleUpdate = () => {
    if (!editingLabel || !editingLabel.name.trim()) {
      toast.error("Please enter a name");
      return;
    }
    updateMutation.mutate({
      id: editingLabel.id,
      name: editingLabel.name.trim(),
    });
  };

  const handleAssign = () => {
    if (!assigningLabel) return;
    assignMutation.mutate({
      labelId: assigningLabel.id,
      productId: selectedProductId,
    });
  };

  const formatDate = (date: Date | null) => {
    if (!date) return "Never";
    return new Date(date).toLocaleString();
  };

  const getBatteryColor = (percent: number | null) => {
    if (percent === null) return "text-muted-foreground";
    if (percent > 50) return "text-green-500";
    if (percent > 20) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Labels</h1>
          <p className="text-muted-foreground">
            Register and manage your electronic shelf labels.
          </p>
        </div>
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Label
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Register a Label</DialogTitle>
              <DialogDescription>
                Enter the serial number of your label device. All your gateways
                will search for it automatically.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="serial">Serial Number</Label>
                <Input
                  id="serial"
                  placeholder="LBL-XXXX-XXXX"
                  value={serialNumber}
                  onChange={(e) =>
                    setSerialNumber(e.target.value.toUpperCase())
                  }
                />
                <p className="text-muted-foreground text-xs">
                  The serial number is printed on the back of your label device.
                </p>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="name">Label Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., Aisle 1 - Shelf 3"
                  value={labelName}
                  onChange={(e) => setLabelName(e.target.value)}
                />
                <p className="text-muted-foreground text-xs">
                  Give your label a friendly name to identify its location.
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleRegister}
                disabled={registerMutation.isPending}
              >
                {registerMutation.isPending
                  ? "Registering..."
                  : "Register Label"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Info Card for pending labels */}
      {labels && labels.filter((l) => l.status === "pending").length > 0 && (
        <Card className="border-yellow-500/50 bg-yellow-500/5">
          <CardContent className="pt-6">
            <div className="flex items-start gap-4">
              <Clock className="mt-0.5 h-5 w-5 text-yellow-500" />
              <div>
                <h4 className="font-medium">Labels Pending Discovery</h4>
                <p className="text-muted-foreground text-sm">
                  {labels.filter((l) => l.status === "pending").length} label(s)
                  are waiting to be found by a gateway. Make sure your gateway
                  is online and the labels are powered on and within range.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Label List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Labels</CardTitle>
          <CardDescription>
            {labels?.length || 0} label{labels?.length !== 1 ? "s" : ""}{" "}
            registered
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-muted-foreground py-8 text-center">
              Loading labels...
            </div>
          ) : labels && labels.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Status</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Serial Number</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Signal</TableHead>
                  <TableHead>Battery</TableHead>
                  <TableHead>Gateway</TableHead>
                  <TableHead>Last Seen</TableHead>
                  <TableHead className="w-[70px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {labels.map((label) => {
                  const status = statusConfig[label.status as LabelStatus];
                  const StatusIcon = status.icon;
                  return (
                    <TableRow key={label.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <StatusIcon
                            className={`h-4 w-4 ${
                              label.status === "updating" ? "animate-spin" : ""
                            }`}
                          />
                          <Badge variant={status.variant}>{status.label}</Badge>
                        </div>
                      </TableCell>
                      <TableCell className="font-medium">
                        {label.name}
                      </TableCell>
                      <TableCell>
                        <code className="bg-muted rounded px-2 py-1 text-xs">
                          {label.serialNumber}
                        </code>
                      </TableCell>
                      <TableCell>
                        {label.product ? (
                          <div className="flex items-center gap-2">
                            <Package className="text-muted-foreground h-4 w-4" />
                            <span>{label.product.name}</span>
                          </div>
                        ) : (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-muted-foreground h-7"
                            onClick={() => {
                              setAssigningLabel({
                                id: label.id,
                                name: label.name,
                                productId: label.productId,
                              });
                              setSelectedProductId(label.productId);
                              setIsAssignOpen(true);
                            }}
                          >
                            <Plus className="mr-1 h-3 w-3" />
                            Assign Product
                          </Button>
                        )}
                      </TableCell>
                      <TableCell>
                        <SignalIndicator rssi={label.rssi} />
                      </TableCell>
                      <TableCell>
                        {label.batteryPercent !== null ? (
                          <div className="flex items-center gap-1">
                            <Battery
                              className={`h-4 w-4 ${getBatteryColor(label.batteryPercent)}`}
                            />
                            <span>{label.batteryPercent}%</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {label.gateway ? (
                          <div className="flex items-center gap-2">
                            <Router className="text-muted-foreground h-4 w-4" />
                            <span className="text-sm">
                              {label.gateway.name}
                            </span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">
                        {formatDate(label.lastSeenAt)}
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
                                setAssigningLabel({
                                  id: label.id,
                                  name: label.name,
                                  productId: label.productId,
                                });
                                setSelectedProductId(label.productId);
                                setIsAssignOpen(true);
                              }}
                            >
                              <Package className="mr-2 h-4 w-4" />
                              Assign Product
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => {
                                setEditingLabel({
                                  id: label.id,
                                  name: label.name,
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
                                    Delete Label
                                  </AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Are you sure you want to delete "
                                    {label.name}"? This action cannot be undone.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction
                                    onClick={() =>
                                      deleteMutation.mutate({ id: label.id })
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
                  );
                })}
              </TableBody>
            </Table>
          ) : (
            <div className="py-12 text-center">
              <Tag className="text-muted-foreground mx-auto mb-4 h-12 w-12" />
              <h3 className="mb-2 text-lg font-semibold">
                No labels registered
              </h3>
              <p className="text-muted-foreground mb-4">
                Register your first label to start displaying products.
              </p>
              <Button onClick={() => setIsAddOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Label
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Label</DialogTitle>
            <DialogDescription>
              Update the name of your label.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-name">Label Name</Label>
              <Input
                id="edit-name"
                value={editingLabel?.name || ""}
                onChange={(e) =>
                  setEditingLabel((prev) =>
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

      {/* Assign Product Dialog */}
      <Dialog open={isAssignOpen} onOpenChange={setIsAssignOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Assign Product</DialogTitle>
            <DialogDescription>
              Select a product to display on "{assigningLabel?.name}". The label
              will update on the next sync with its gateway.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="product">Product</Label>
              <Select
                value={selectedProductId || "none"}
                onValueChange={(value) =>
                  setSelectedProductId(value === "none" ? null : value)
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a product" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">
                    <span className="text-muted-foreground">
                      No product (blank label)
                    </span>
                  </SelectItem>
                  {products?.map((product) => (
                    <SelectItem key={product.id} value={product.id}>
                      {product.name}
                      {product.brand && (
                        <span className="text-muted-foreground ml-2">
                          ({product.brand})
                        </span>
                      )}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {(!products || products.length === 0) && (
                <p className="text-muted-foreground text-xs">
                  No products available. Create a product first.
                </p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAssignOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAssign} disabled={assignMutation.isPending}>
              {assignMutation.isPending ? "Assigning..." : "Assign Product"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
