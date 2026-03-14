import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Modal } from './ui/modal';
import { setPrice } from '../data/backendApi';
import { useLiveBattery } from '../hooks/useLiveBattery';
import type {
  Gateway,
  Product,
  Promotion,
  ShelfLocation,
  Store,
  Tag,
  TagPayload,
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
  tagPayloads: TagPayload[];
  promotions: Promotion[];
}

export function DashboardPage({
  stores,
  gateways,
  shelfLocations,
  products,
  tags,
  tagPayloads,
  promotions,
}: DashboardPageProps): JSX.Element {
  const { battery, isConnected } = useLiveBattery();
  const [isPriceModalOpen, setIsPriceModalOpen] = useState(false);
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
    // Basic guard to avoid unnecessary network calls with empty values.
    if (!priceValue.trim()) {
      setPriceFeedback('Please enter a price value.');
      return;
    }

    setIsSubmittingPrice(true);
    setPriceFeedback(null);
    try {
      // Delegates to backend API client (`POST /set_price`).
      await setPrice(priceValue.trim());
      setPriceFeedback('Price update sent to the backend and gateway.');
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

      <Card className="space-y-3 rounded-xl">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold">Payload readiness</h4>
          <p className="text-sm text-muted-foreground">{tagPayloads.length} payload templates available</p>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {tagPayloads.map((payload) => (
            <div key={payload.id} className="rounded-lg border border-border bg-background p-3">
              <p className="font-medium">{payload.id}</p>
              <p className="text-xs text-muted-foreground">{JSON.stringify(payload.payloadJson)}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card className="space-y-4 rounded-xl">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold">Live device control</h4>
          <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${isConnected ? 'border-primary/30 bg-primary/10 text-foreground' : 'border-border bg-background text-muted-foreground'}`}>
            {isConnected ? 'Socket connected' : 'Socket disconnected'}
          </span>
        </div>
        <div className="rounded-lg border border-border bg-background p-4">
          <p className="text-sm text-muted-foreground">Latest battery report</p>
          {/* Value comes from backend `/battery` + Socket.IO `battery_update` events. */}
          <p className="text-2xl font-semibold">{battery ?? 'No data'}{typeof battery === 'number' ? '%' : ''}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" onClick={() => setIsPriceModalOpen(true)}>
            Set Price
          </Button>
          <p className="text-xs text-muted-foreground">Sends `POST /set_price` like the backend demo page.</p>
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
            <Button size="sm" onClick={() => void submitPrice()} disabled={isSubmittingPrice}>
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
}

export function TagsPage({ tags }: TagsPageProps): JSX.Element {
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
              <p className="text-sm text-muted-foreground">Product: {tag.productId} · Location: {tag.shelfLocationId}</p>
              <p className="text-sm text-muted-foreground">Battery: {tag.batteryPct}%</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`inline-flex rounded-full border px-2 py-1 text-xs font-medium ${statusPillClass(tag.status)}`}>
                {tag.status}
              </span>
              <Button variant="outline" size="sm">
                Inspect
              </Button>
            </div>
          </div>
        ))}
      </Card>
    </section>
  );
}

export interface TagPayloadsPageProps {
  tagPayloads: TagPayload[];
}

export function TagPayloadsPage({ tagPayloads }: TagPayloadsPageProps): JSX.Element {
  return (
    <section className="space-y-4">
      <SectionHeader
        title="Tag payload templates"
        description="Review payload structures that are rendered and sent to shelf labels."
        primaryAction="Create template"
      />
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        {tagPayloads.map((tagPayload) => (
          <Card key={tagPayload.id} className="space-y-2 rounded-xl">
            <p className="font-medium">{tagPayload.id}</p>
            <p className="text-sm text-muted-foreground">{JSON.stringify(tagPayload.payloadJson)}</p>
          </Card>
        ))}
      </div>
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
