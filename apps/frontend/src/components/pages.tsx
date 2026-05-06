import { useState } from 'react';
import { useSWRConfig } from 'swr';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Modal } from './ui/modal';
import { updateProductPrice, updateTagProductAssignment } from '../data/backendApi';
import type {
  Gateway,
  Product,
  Promotion,
  ShelfLocation,
  Store,
  Tag,
} from '../types';

function formatMoney(value: number): string {
  return `$${value.toFixed(2)}`;
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString();
}

function statusPillClass(status: string): string {
  switch (status) {
    case 'online':
    case 'active':
      return 'border-primary/30 bg-primary/10 text-foreground';
    case 'degraded':
    case 'low-battery':
      return 'border-border bg-muted text-foreground';
    default:
      return 'border-border bg-background text-muted-foreground';
  }
}

interface SectionHeaderProps {
  title: string;
  description: string;
  primaryAction?: string;
  secondaryAction?: string;
}

function SectionHeader({ title, description, primaryAction, secondaryAction }: SectionHeaderProps): JSX.Element {
  return (
    <header className="flex flex-col gap-3 rounded-xl border border-border bg-card p-5 md:flex-row md:items-center md:justify-between">
      <div>
        <h3 className="text-xl font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {(primaryAction || secondaryAction) && (
        <div className="flex items-center gap-2">
          {secondaryAction ? (
            <Button variant="outline" size="sm">
              {secondaryAction}
            </Button>
          ) : null}
          {primaryAction ? <Button size="sm">{primaryAction}</Button> : null}
        </div>
      )}
    </header>
  );
}

interface MetricCardProps {
  label: string;
  value: string | number;
  hint: string;
}

function MetricCard({ label, value, hint }: MetricCardProps): JSX.Element {
  return (
    <Card className="space-y-2 rounded-xl">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-semibold">{value}</p>
      <p className="text-xs text-muted-foreground">{hint}</p>
    </Card>
  );
}

export interface DashboardPageProps {
  stores: Store[];
  gateways: Gateway[];
  shelfLocations: ShelfLocation[];
  products: Product[];
  tags: Tag[];
  promotions: Promotion[];
  isRealtimeConnected: boolean;
  lastBatteryUpdate: { tagId: number; batteryPct: number } | null;
}

export function DashboardPage({
  stores,
  gateways,
  shelfLocations,
  products,
  tags,
  promotions,
  isRealtimeConnected,
  lastBatteryUpdate,
}: DashboardPageProps): JSX.Element {
  const [isPriceModalOpen, setIsPriceModalOpen] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [priceValue, setPriceValue] = useState('');
  const [isSubmittingPrice, setIsSubmittingPrice] = useState(false);
  const [priceFeedback, setPriceFeedback] = useState<string | null>(null);

  const gatewaysOnline = gateways.filter((gateway) => gateway.status === 'online').length;
  const gatewaysAttention = gateways.filter((gateway) => gateway.status !== 'online').length;
  const tagsNeedingAttention = tags.filter((tag) => tag.status !== 'active').length;
  const activePromotions = promotions.filter(
    (promotion) => Date.now() >= Date.parse(promotion.startAt) && Date.now() <= Date.parse(promotion.endAt)
  ).length;
  const productById = new Map(products.map((product) => [product.id, product]));
  const shelfLocationById = new Map(shelfLocations.map((shelfLocation) => [shelfLocation.id, shelfLocation]));

  const submitPrice = async (): Promise<void> => {
    const productId = Number(selectedProductId);
    if (!Number.isInteger(productId) || productId <= 0) {
      setPriceFeedback('Please select a product first.');
      return;
    }

    // Basic guard to avoid unnecessary network calls with empty values.
    if (!priceValue.trim()) {
      setPriceFeedback('Please enter a price value.');
      return;
    }

    const parsedPrice = Number(priceValue.trim());
    if (!Number.isFinite(parsedPrice) || parsedPrice < 0) {
      setPriceFeedback('Please enter a valid non-negative price.');
      return;
    }

    setIsSubmittingPrice(true);
    setPriceFeedback(null);
    try {
      // Uses the real product update API, which also triggers payload publishing for assigned tags.
      const updatedProduct = await updateProductPrice(productId, parsedPrice);
      setPriceFeedback(`Updated ${updatedProduct.name} to ${formatMoney(updatedProduct.price)}.`);
      setPriceValue('');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to send price update.';
      setPriceFeedback(message);
    } finally {
      setIsSubmittingPrice(false);
    }
  };

  return (
    <section className="space-y-4">
      <SectionHeader
        title="Fleet overview"
        description="Monitor store coverage, gateway health, and label readiness across your electronic shelf label network."
        secondaryAction="Export snapshot"
        primaryAction="Sync updates"
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Stores" value={stores.length} hint="Active locations with connected ESL infrastructure" />
        <MetricCard label="Gateways online" value={`${gatewaysOnline}/${gateways.length}`} hint={`${gatewaysAttention} require attention`} />
        <MetricCard label="Tags needing attention" value={tagsNeedingAttention} hint="Low battery or offline labels" />
        <MetricCard label="Active promotions" value={activePromotions} hint="Campaigns currently affecting shelf pricing" />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card className="space-y-4 rounded-xl">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold">Network health</h4>
            <Button variant="outline" size="sm">
              View gateways
            </Button>
          </div>
          <div className="space-y-3">
            {gateways.map((gateway) => (
              <div key={gateway.id} className="flex items-center justify-between rounded-lg border border-border bg-background px-3 py-2">
                <div>
                  <p className="font-medium">{gateway.id}</p>
                  <p className="text-sm text-muted-foreground">Store {gateway.storeId}</p>
                </div>
                <div className="text-right">
                  <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${statusPillClass(gateway.status)}`}>
                    {gateway.status}
                  </span>
                  <p className="mt-1 text-xs text-muted-foreground">Heartbeat {formatDateTime(gateway.lastHeartbeatAt)}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="space-y-4 rounded-xl">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold">Label content queue</h4>
            <Button size="sm">Publish all</Button>
          </div>
          <div className="space-y-3">
            {tags.map((tag) => {
              const product = tag.productId === null ? undefined : productById.get(tag.productId);
              const shelfLocation = tag.shelfLocationId === null ? undefined : shelfLocationById.get(tag.shelfLocationId);
              return (
                <div key={tag.id} className="rounded-lg border border-border bg-background px-3 py-2">
                  <div className="flex items-center justify-between gap-2">
                    <p className="font-medium">{product?.name ?? tag.productId ?? 'Unassigned product'}</p>
                    <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${statusPillClass(tag.status)}`}>
                      {tag.status}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {tag.id} · {shelfLocation ? `Aisle ${shelfLocation.aisle}, ${shelfLocation.level}` : tag.shelfLocationId} · Battery {tag.batteryPct}%
                  </p>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      <Card className="space-y-4 rounded-xl">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold">Live device control</h4>
          <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${isRealtimeConnected ? 'border-primary/30 bg-primary/10 text-foreground' : 'border-border bg-background text-muted-foreground'}`}>
            {isRealtimeConnected ? 'Socket connected' : 'Socket disconnected'}
          </span>
        </div>
        <div className="rounded-lg border border-border bg-background p-4">
          <p className="text-sm text-muted-foreground">Latest MQTT battery update</p>
          <p className="text-2xl font-semibold">
            {lastBatteryUpdate ? `Tag ${lastBatteryUpdate.tagId}: ${lastBatteryUpdate.batteryPct}%` : 'No live updates yet'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" onClick={() => setIsPriceModalOpen(true)}>
            Set Price
          </Button>
          <p className="text-xs text-muted-foreground">Updates a product through `PATCH /api/products/:productId`.</p>
        </div>
      </Card>

      <Modal
        open={isPriceModalOpen}
        title="Send price update"
        description="Push a new price to the backend, then onward to gateway/tag over MQTT."
        onClose={() => {
          setIsPriceModalOpen(false);
          setPriceFeedback(null);
        }}
      >
        <div className="space-y-3">
          <label className="block text-sm text-muted-foreground" htmlFor="price-product-select">
            Product
          </label>
          <select
            id="price-product-select"
            value={selectedProductId}
            onChange={(event) => setSelectedProductId(event.target.value)}
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">Select a product</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name} ({product.sku})
              </option>
            ))}
          </select>
          <label className="block text-sm text-muted-foreground" htmlFor="price-input">
            Price
          </label>
          <input
            id="price-input"
            type="number"
            step="0.01"
            min="0"
            value={priceValue}
            onChange={(event) => setPriceValue(event.target.value)}
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
            placeholder="Enter a new shelf price"
          />
          {priceFeedback ? <p className="text-sm text-muted-foreground">{priceFeedback}</p> : null}
          <div className="flex items-center justify-end gap-2">
            <Button variant="outline" size="sm" onClick={() => setIsPriceModalOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={() => void submitPrice()} disabled={isSubmittingPrice || products.length === 0}>
              {isSubmittingPrice ? 'Sending...' : 'Send Price'}
            </Button>
          </div>
        </div>
      </Modal>
    </section>
  );
}
export interface StoresPageProps {
  stores: Store[];
}

export function StoresPage({ stores }: StoresPageProps): JSX.Element {
  return (
    <section className="space-y-4">
      <SectionHeader
        title="Stores"
        description="Manage store locations that use electronic shelf labels."
        primaryAction="Add store"
      />
      <Card className="space-y-3 rounded-xl">
        {stores.map((store) => (
          <div key={store.id} className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-3">
            <div>
              <p className="font-medium">{store.name}</p>
              <p className="text-sm text-muted-foreground">Store ID: {store.id}</p>
            </div>
            <Button variant="outline" size="sm">
              Open
            </Button>
          </div>
        ))}
      </Card>
    </section>
  );
}

export interface GatewaysPageProps {
  gateways: Gateway[];
}

export function GatewaysPage({ gateways }: GatewaysPageProps): JSX.Element {
  return (
    <section className="space-y-4">
      <SectionHeader
        title="Gateways"
        description="Track gateway connectivity and last heartbeat timestamps."
        primaryAction="Register gateway"
      />
      <Card className="space-y-3 rounded-xl">
        {gateways.map((gateway) => (
          <div key={gateway.id} className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-3">
            <div>
              <p className="font-medium">{gateway.id}</p>
              <p className="text-sm text-muted-foreground">Store: {gateway.storeId}</p>
              <p className="text-sm text-muted-foreground">Last heartbeat: {formatDateTime(gateway.lastHeartbeatAt)}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${statusPillClass(gateway.status)}`}>
                {gateway.status}
              </span>
              <Button variant="outline" size="sm">
                Manage
              </Button>
            </div>
          </div>
        ))}
      </Card>
    </section>
  );
}

export interface ShelfLocationsPageProps {
  shelfLocations: ShelfLocation[];
}

export function ShelfLocationsPage({ shelfLocations }: ShelfLocationsPageProps): JSX.Element {
  return (
    <section className="space-y-4">
      <SectionHeader
        title="Shelf locations"
        description="Define aisle and shelf-level coordinates for each store."
        primaryAction="Add location"
      />
      <Card className="space-y-3 rounded-xl">
        {shelfLocations.map((shelfLocation) => (
          <div key={shelfLocation.id} className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-3">
            <div>
              <p className="font-medium">{shelfLocation.id}</p>
              <p className="text-sm text-muted-foreground">Store: {shelfLocation.storeId}</p>
              <p className="text-sm text-muted-foreground">Aisle {shelfLocation.aisle} · Level {shelfLocation.level}</p>
            </div>
            <Button variant="secondary" size="sm">
              Edit
            </Button>
          </div>
        ))}
      </Card>
    </section>
  );
}

export interface ProductsPageProps {
  products: Product[];
}

export function ProductsPage({ products }: ProductsPageProps): JSX.Element {
  return (
    <section className="space-y-4">
      <SectionHeader
        title="Products"
        description="Maintain product catalog data used for shelf labels and pricing payloads."
        primaryAction="Create product"
      />
      <Card className="space-y-3 rounded-xl">
        {products.map((product) => (
          <div key={product.id} className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-3">
            <div>
              <p className="font-medium">{product.name}</p>
              <p className="text-sm text-muted-foreground">SKU: {product.sku} · Product ID: {product.id}</p>
              <p className="text-sm text-muted-foreground">Attributes: {JSON.stringify(product.attributesJson)}</p>
            </div>
            <div className="text-right">
              <p className="font-semibold">{formatMoney(product.price)}</p>
              <Button size="sm" className="mt-2">
                Edit
              </Button>
            </div>
          </div>
        ))}
      </Card>
    </section>
  );
}

export interface TagsPageProps {
  tags: Tag[];
  products: Product[];
}

export function TagsPage({ tags, products }: TagsPageProps): JSX.Element {
  const { mutate } = useSWRConfig();
  const [isInspectModalOpen, setIsInspectModalOpen] = useState(false);
  const [selectedTag, setSelectedTag] = useState<Tag | null>(null);
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [isSubmittingAssignment, setIsSubmittingAssignment] = useState(false);
  const [assignmentFeedback, setAssignmentFeedback] = useState<string | null>(null);

  const productById = new Map(products.map((product) => [product.id, product]));

  const openInspectModal = (tag: Tag): void => {
    setSelectedTag(tag);
    setSelectedProductId(tag.productId === null ? '' : String(tag.productId));
    setAssignmentFeedback(null);
    setIsInspectModalOpen(true);
  };

  const closeInspectModal = (): void => {
    setIsInspectModalOpen(false);
    setSelectedTag(null);
    setSelectedProductId('');
    setAssignmentFeedback(null);
  };

  const submitAssignment = async (): Promise<void> => {
    if (!selectedTag) {
      return;
    }

    const nextProductId = selectedProductId.trim() === '' ? null : Number(selectedProductId);
    if (nextProductId !== null && (!Number.isInteger(nextProductId) || nextProductId <= 0)) {
      setAssignmentFeedback('Please choose a valid product.');
      return;
    }

    setIsSubmittingAssignment(true);
    setAssignmentFeedback(null);
    try {
      const updatedTag = await updateTagProductAssignment(selectedTag.id, nextProductId);
      setSelectedTag(updatedTag);
      setSelectedProductId(updatedTag.productId === null ? '' : String(updatedTag.productId));
      setAssignmentFeedback(
        updatedTag.productId === null
          ? `Tag ${updatedTag.id} is now unassigned.`
          : `Tag ${updatedTag.id} is now assigned to ${productById.get(updatedTag.productId)?.name ?? `product ${updatedTag.productId}`}.`
      );
      await mutate('tags');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to update tag assignment.';
      setAssignmentFeedback(message);
    } finally {
      setIsSubmittingAssignment(false);
    }
  };

  return (
    <section className="space-y-4">
      <SectionHeader
        title="Tags"
        description="Monitor label battery health, assignment, and connectivity state."
        primaryAction="Pair tag"
      />
      <Card className="space-y-3 rounded-xl">
        {tags.map((tag) => (
          <div key={tag.id} className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-3">
            <div>
              <p className="font-medium">{tag.id}</p>
              <p className="text-sm text-muted-foreground">
                Product: {tag.productId === null ? 'Unassigned' : productById.get(tag.productId)?.name ?? `#${tag.productId}`}
                {' · '}
                Location: {tag.shelfLocationId === null ? 'Unassigned' : `#${tag.shelfLocationId}`}
              </p>
              <p className="text-sm text-muted-foreground">Battery: {tag.batteryPct}%</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${statusPillClass(tag.status)}`}>
                {tag.status}
              </span>
              <Button variant="outline" size="sm" onClick={() => openInspectModal(tag)}>
                Inspect
              </Button>
            </div>
          </div>
        ))}
      </Card>

      <Modal
        open={isInspectModalOpen}
        title={selectedTag ? `Inspect tag ${selectedTag.id}` : 'Inspect tag'}
        description="Review the current assignment and move this tag to another product if needed."
        onClose={closeInspectModal}
      >
        {selectedTag ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-3 rounded-lg border border-border bg-background p-3 text-sm md:grid-cols-2">
              <div>
                <p className="text-muted-foreground">Tag ID</p>
                <p className="font-medium">{selectedTag.id}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Status</p>
                <p className="font-medium">{selectedTag.status}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Battery</p>
                <p className="font-medium">{selectedTag.batteryPct}%</p>
              </div>
              <div>
                <p className="text-muted-foreground">Current product</p>
                <p className="font-medium">
                  {selectedTag.productId === null
                    ? 'Unassigned'
                    : productById.get(selectedTag.productId)?.name ?? `#${selectedTag.productId}`}
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm text-muted-foreground" htmlFor="tag-product-select">
                Assign product
              </label>
              <select
                id="tag-product-select"
                value={selectedProductId}
                onChange={(event) => setSelectedProductId(event.target.value)}
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              >
                <option value="">Unassigned</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.sku})
                  </option>
                ))}
              </select>
              <p className="text-xs text-muted-foreground">
                Saving a new product assignment will republish the tag payload from the backend.
              </p>
            </div>

            {assignmentFeedback ? <p className="text-sm text-muted-foreground">{assignmentFeedback}</p> : null}

            <div className="flex items-center justify-end gap-2">
              <Button variant="outline" size="sm" onClick={closeInspectModal}>
                Close
              </Button>
              <Button
                size="sm"
                onClick={() => void submitAssignment()}
                disabled={isSubmittingAssignment || products.length === 0}
              >
                {isSubmittingAssignment ? 'Saving...' : 'Save assignment'}
              </Button>
            </div>
          </div>
        ) : null}
      </Modal>
    </section>
  );
}

export interface PromotionsPageProps {
  promotions: Promotion[];
}

export function PromotionsPage({ promotions }: PromotionsPageProps): JSX.Element {
  return (
    <section className="space-y-4">
      <SectionHeader
        title="Promotions"
        description="Schedule promotional rules and align campaign priority before publishing to labels."
        primaryAction="Create promotion"
      />
      <Card className="space-y-3 rounded-xl">
        {promotions.map((promotion) => (
          <div key={promotion.id} className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-3">
            <div>
              <p className="font-medium">{promotion.id}</p>
              <p className="text-sm text-muted-foreground">Product: {promotion.productId} · Type: {promotion.promoType}</p>
              <p className="text-sm text-muted-foreground">
                Active: {formatDateTime(promotion.startAt)} - {formatDateTime(promotion.endAt)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Priority {promotion.priority}</p>
              <p className="font-semibold">Value {promotion.value}</p>
              <Button size="sm" className="mt-2">
                Schedule
              </Button>
            </div>
          </div>
        ))}
      </Card>
    </section>
  );
}
