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
import { Textarea } from "@/components/ui/textarea";
import type { ProductPriceDetails } from "@/services/product/product.schema";
import { api } from "@/trpc/react";
import {
  Barcode,
  MoreHorizontal,
  Package,
  Pencil,
  Percent,
  Plus,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const CURRENCIES = [
  {
    code: "SEK",
    symbol: { suffix: " kr" },
    decimalPlaces: 2,
    label: "Swedish Krona (SEK)",
  },
  {
    code: "USD",
    symbol: { prefix: "$" },
    decimalPlaces: 2,
    label: "US Dollar (USD)",
  },
  {
    code: "EUR",
    symbol: { prefix: "€" },
    decimalPlaces: 2,
    label: "Euro (EUR)",
  },
  {
    code: "GBP",
    symbol: { prefix: "£" },
    decimalPlaces: 2,
    label: "British Pound (GBP)",
  },
  {
    code: "NOK",
    symbol: { suffix: " kr" },
    decimalPlaces: 2,
    label: "Norwegian Krone (NOK)",
  },
  {
    code: "DKK",
    symbol: { suffix: " kr" },
    decimalPlaces: 2,
    label: "Danish Krone (DKK)",
  },
];

const UNITS = [
  { value: "unit", label: "Unit" },
  { value: "piece", label: "Piece" },
  { value: "kg", label: "Kilogram (kg)" },
  { value: "g", label: "Gram (g)" },
  { value: "l", label: "Liter (l)" },
  { value: "ml", label: "Milliliter (ml)" },
  { value: "m", label: "Meter (m)" },
  { value: "cm", label: "Centimeter (cm)" },
];

interface ProductFormData {
  name: string;
  brand: string;
  barcode: string;
  sku: string;
  description: string;
  currency: string;
  price: string;
  priceUnit: string;
  quantity: string;
  quantityUnit: string;
  discountPercentage: string;
  discountValidUntil: string;
}

const defaultFormData: ProductFormData = {
  name: "",
  brand: "",
  barcode: "",
  sku: "",
  description: "",
  currency: "SEK",
  price: "",
  priceUnit: "unit",
  quantity: "1",
  quantityUnit: "unit",
  discountPercentage: "",
  discountValidUntil: "",
};

export function ProductsContent() {
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [formData, setFormData] = useState<ProductFormData>(defaultFormData);
  const [editingProductId, setEditingProductId] = useState<string | null>(null);

  const utils = api.useUtils();
  const { data: products, isLoading } = api.product.readAll.useQuery();

  const createMutation = api.product.create.useMutation({
    onSuccess: () => {
      toast.success("Product created successfully!");
      setIsAddOpen(false);
      setFormData(defaultFormData);
      utils.product.readAll.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const updateMutation = api.product.update.useMutation({
    onSuccess: () => {
      toast.success("Product updated successfully!");
      setIsEditOpen(false);
      setEditingProductId(null);
      setFormData(defaultFormData);
      utils.product.readAll.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const deleteMutation = api.product.delete.useMutation({
    onSuccess: () => {
      toast.success("Product deleted successfully!");
      utils.product.readAll.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const buildPriceDetails = (): ProductPriceDetails => {
    const currency =
      CURRENCIES.find((c) => c.code === formData.currency) || CURRENCIES[0]!;
    const priceValue = parseFloat(formData.price) || 0;
    const priceInCents = Math.round(
      priceValue * Math.pow(10, currency.decimalPlaces),
    );

    const priceDetails: ProductPriceDetails = {
      currency: {
        code: currency.code,
        symbol: currency.symbol,
        decimalPlaces: currency.decimalPlaces,
      },
      priceInCents,
      priceUnit: formData.priceUnit as ProductPriceDetails["priceUnit"],
      quantity: parseFloat(formData.quantity) || 1,
      quantityUnit:
        formData.quantityUnit as ProductPriceDetails["quantityUnit"],
    };

    if (formData.discountPercentage && formData.discountValidUntil) {
      priceDetails.discount = {
        percentage: parseFloat(formData.discountPercentage),
        validUntil: formData.discountValidUntil,
      };
    }

    return priceDetails;
  };

  const handleCreate = () => {
    if (!formData.name.trim()) {
      toast.error("Please enter a product name");
      return;
    }
    if (!formData.price || parseFloat(formData.price) <= 0) {
      toast.error("Please enter a valid price");
      return;
    }

    createMutation.mutate({
      name: formData.name.trim(),
      brand: formData.brand.trim() || undefined,
      barcode: formData.barcode.trim() || undefined,
      sku: formData.sku.trim() || undefined,
      description: formData.description.trim() || undefined,
      priceDetails: buildPriceDetails(),
    });
  };

  const handleUpdate = () => {
    if (!editingProductId) return;
    if (!formData.name.trim()) {
      toast.error("Please enter a product name");
      return;
    }
    if (!formData.price || parseFloat(formData.price) <= 0) {
      toast.error("Please enter a valid price");
      return;
    }

    updateMutation.mutate({
      id: editingProductId,
      name: formData.name.trim(),
      brand: formData.brand.trim() || null,
      barcode: formData.barcode.trim() || null,
      sku: formData.sku.trim() || null,
      description: formData.description.trim() || null,
      priceDetails: buildPriceDetails(),
    });
  };

  const openEditDialog = (product: NonNullable<typeof products>[number]) => {
    const pd = product.priceDetails as ProductPriceDetails;
    const priceValue =
      pd.priceInCents / Math.pow(10, pd.currency.decimalPlaces);

    setFormData({
      name: product.name,
      brand: product.brand || "",
      barcode: product.barcode || "",
      sku: product.sku || "",
      description: product.description || "",
      currency: pd.currency.code,
      price: priceValue.toString(),
      priceUnit: pd.priceUnit,
      quantity: pd.quantity.toString(),
      quantityUnit: pd.quantityUnit,
      discountPercentage: pd.discount?.percentage.toString() || "",
      discountValidUntil: pd.discount?.validUntil || "",
    });
    setEditingProductId(product.id);
    setIsEditOpen(true);
  };

  const formatPrice = (priceDetails: ProductPriceDetails) => {
    const value =
      priceDetails.priceInCents /
      Math.pow(10, priceDetails.currency.decimalPlaces);
    const formatted = value.toFixed(priceDetails.currency.decimalPlaces);
    const prefix = priceDetails.currency.symbol.prefix || "";
    const suffix = priceDetails.currency.symbol.suffix || "";
    return `${prefix}${formatted}${suffix}`;
  };

  const updateFormField = (field: keyof ProductFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const ProductForm = ({
    onSubmit,
    submitLabel,
    isPending,
  }: {
    onSubmit: () => void;
    submitLabel: string;
    isPending: boolean;
  }) => (
    <div className="grid max-h-[60vh] gap-4 overflow-y-auto py-4 pr-2">
      {/* Basic Info */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="grid gap-2">
          <Label htmlFor="name">Product Name *</Label>
          <Input
            id="name"
            placeholder="e.g., Chicken Breast"
            value={formData.name}
            onChange={(e) => updateFormField("name", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="brand">Brand</Label>
          <Input
            id="brand"
            placeholder="e.g., Fresh Farm"
            value={formData.brand}
            onChange={(e) => updateFormField("brand", e.target.value)}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="grid gap-2">
          <Label htmlFor="barcode">Barcode (EAN/UPC)</Label>
          <Input
            id="barcode"
            placeholder="e.g., 7350123456789"
            value={formData.barcode}
            onChange={(e) => updateFormField("barcode", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="sku">SKU</Label>
          <Input
            id="sku"
            placeholder="e.g., CHK-BRST-001"
            value={formData.sku}
            onChange={(e) => updateFormField("sku", e.target.value)}
          />
        </div>
      </div>

      <div className="grid gap-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          placeholder="Product description..."
          value={formData.description}
          onChange={(e) => updateFormField("description", e.target.value)}
          rows={2}
        />
      </div>

      {/* Pricing */}
      <div className="border-t pt-4">
        <h4 className="mb-4 font-medium">Pricing</h4>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="grid gap-2">
            <Label htmlFor="price">Price *</Label>
            <Input
              id="price"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={formData.price}
              onChange={(e) => updateFormField("price", e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="currency">Currency</Label>
            <Select
              value={formData.currency}
              onValueChange={(v) => updateFormField("currency", v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CURRENCIES.map((c) => (
                  <SelectItem key={c.code} value={c.code}>
                    {c.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="priceUnit">Price Per</Label>
            <Select
              value={formData.priceUnit}
              onValueChange={(v) => updateFormField("priceUnit", v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {UNITS.map((u) => (
                  <SelectItem key={u.value} value={u.value}>
                    {u.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Quantity */}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="grid gap-2">
          <Label htmlFor="quantity">Package Quantity</Label>
          <Input
            id="quantity"
            type="number"
            step="0.01"
            min="0"
            placeholder="1"
            value={formData.quantity}
            onChange={(e) => updateFormField("quantity", e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <Label htmlFor="quantityUnit">Quantity Unit</Label>
          <Select
            value={formData.quantityUnit}
            onValueChange={(v) => updateFormField("quantityUnit", v)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {UNITS.map((u) => (
                <SelectItem key={u.value} value={u.value}>
                  {u.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Discount */}
      <div className="border-t pt-4">
        <h4 className="mb-4 font-medium">Discount (Optional)</h4>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="grid gap-2">
            <Label htmlFor="discountPercentage">Discount %</Label>
            <Input
              id="discountPercentage"
              type="number"
              step="1"
              min="0"
              max="100"
              placeholder="e.g., 10"
              value={formData.discountPercentage}
              onChange={(e) =>
                updateFormField("discountPercentage", e.target.value)
              }
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="discountValidUntil">Valid Until</Label>
            <Input
              id="discountValidUntil"
              type="date"
              value={formData.discountValidUntil}
              onChange={(e) =>
                updateFormField("discountValidUntil", e.target.value)
              }
            />
          </div>
        </div>
      </div>

      <DialogFooter className="pt-4">
        <Button
          variant="outline"
          onClick={() => {
            setIsAddOpen(false);
            setIsEditOpen(false);
            setFormData(defaultFormData);
            setEditingProductId(null);
          }}
        >
          Cancel
        </Button>
        <Button onClick={onSubmit} disabled={isPending}>
          {isPending ? "Saving..." : submitLabel}
        </Button>
      </DialogFooter>
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Products</h1>
          <p className="text-muted-foreground">
            Create and manage products to display on your labels.
          </p>
        </div>
        <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Product
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Product</DialogTitle>
              <DialogDescription>
                Add a new product to your catalog. Products can be assigned to
                labels.
              </DialogDescription>
            </DialogHeader>
            <ProductForm
              onSubmit={handleCreate}
              submitLabel="Create Product"
              isPending={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Product List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Products</CardTitle>
          <CardDescription>
            {products?.length || 0} product{products?.length !== 1 ? "s" : ""}{" "}
            in catalog
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-muted-foreground py-8 text-center">
              Loading products...
            </div>
          ) : products && products.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead>Barcode</TableHead>
                  <TableHead>Price</TableHead>
                  <TableHead>Discount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[70px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {products.map((product) => {
                  const pd = product.priceDetails as ProductPriceDetails;
                  return (
                    <TableRow key={product.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{product.name}</p>
                          {product.brand && (
                            <p className="text-muted-foreground text-sm">
                              {product.brand}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {product.barcode ? (
                          <div className="flex items-center gap-2">
                            <Barcode className="text-muted-foreground h-4 w-4" />
                            <code className="text-xs">{product.barcode}</code>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{formatPrice(pd)}</span>
                        <span className="text-muted-foreground text-sm">
                          /{pd.priceUnit}
                        </span>
                      </TableCell>
                      <TableCell>
                        {pd.discount ? (
                          <div className="flex items-center gap-1">
                            <Percent className="h-4 w-4 text-green-500" />
                            <span className="font-medium text-green-500">
                              {pd.discount.percentage}% off
                            </span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={product.isActive ? "default" : "secondary"}
                        >
                          {product.isActive ? "Active" : "Inactive"}
                        </Badge>
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
                              onClick={() => openEditDialog(product)}
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
                                    Delete Product
                                  </AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Are you sure you want to delete "
                                    {product.name}"? This action cannot be
                                    undone. Labels using this product will show
                                    blank.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction
                                    onClick={() =>
                                      deleteMutation.mutate({ id: product.id })
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
              <Package className="text-muted-foreground mx-auto mb-4 h-12 w-12" />
              <h3 className="mb-2 text-lg font-semibold">No products yet</h3>
              <p className="text-muted-foreground mb-4">
                Create your first product to assign to labels.
              </p>
              <Button onClick={() => setIsAddOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Add Product
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Product</DialogTitle>
            <DialogDescription>Update product information.</DialogDescription>
          </DialogHeader>
          <ProductForm
            onSubmit={handleUpdate}
            submitLabel="Save Changes"
            isPending={updateMutation.isPending}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
