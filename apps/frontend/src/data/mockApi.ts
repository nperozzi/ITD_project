import type {
  Gateway,
  Product,
  Promotion,
  ShelfLocation,
  Store,
  Tag,
  TagPayload,
} from '../types';

const stores: Store[] = [
  { id: 'store-001', name: 'Downtown Market' },
  { id: 'store-002', name: 'Riverside Market' },
];

const gateways: Gateway[] = [
  {
    id: 'gw-001',
    storeId: 'store-001',
    status: 'online',
    lastHeartbeatAt: '2026-02-26T09:15:00Z',
  },
  {
    id: 'gw-002',
    storeId: 'store-001',
    status: 'degraded',
    lastHeartbeatAt: '2026-02-26T09:10:00Z',
  },
  {
    id: 'gw-003',
    storeId: 'store-002',
    status: 'offline',
    lastHeartbeatAt: '2026-02-26T08:02:00Z',
  },
];

const shelfLocations: ShelfLocation[] = [
  { id: 'sl-001', storeId: 'store-001', aisle: 'A1', level: 'L1' },
  { id: 'sl-002', storeId: 'store-001', aisle: 'A2', level: 'L2' },
  { id: 'sl-003', storeId: 'store-002', aisle: 'B1', level: 'L1' },
];

const products: Product[] = [
  {
    id: 'prd-001',
    sku: 'CF-AR-1KG',
    name: 'Arabica Coffee Beans',
    attributesJson: { roast: 'medium', origin: 'Colombia', organic: true },
    price: 22.9,
  },
  {
    id: 'prd-002',
    sku: 'ML-OT-1L',
    name: 'Organic Oat Milk',
    attributesJson: { dairyFree: true, volumeMl: 1000 },
    price: 4.5,
  },
  {
    id: 'prd-003',
    sku: 'CH-DK-90G',
    name: 'Dark Chocolate Bar',
    attributesJson: { cocoaPct: 75, vegan: true },
    price: 3.2,
  },
];

const tags: Tag[] = [
  {
    id: 'tag-001',
    batteryPct: 88,
    status: 'active',
    productId: 'prd-001',
    shelfLocationId: 'sl-001',
  },
  {
    id: 'tag-002',
    batteryPct: 24,
    status: 'low-battery',
    productId: 'prd-002',
    shelfLocationId: 'sl-002',
  },
  {
    id: 'tag-003',
    batteryPct: 0,
    status: 'offline',
    productId: 'prd-003',
    shelfLocationId: 'sl-003',
  },
];

const tagPayloads: TagPayload[] = [
  {
    id: 'tp-001',
    payloadJson: { tagId: 'tag-001', title: 'Arabica Coffee Beans', price: 22.9 },
  },
  {
    id: 'tp-002',
    payloadJson: { tagId: 'tag-002', title: 'Organic Oat Milk', price: 4.5 },
  },
];

const promotions: Promotion[] = [
  {
    id: 'promo-001',
    productId: 'prd-001',
    promoType: 'percentage',
    value: 10,
    startAt: '2026-02-25T00:00:00Z',
    endAt: '2026-03-03T23:59:59Z',
    priority: 1,
  },
  {
    id: 'promo-002',
    productId: 'prd-003',
    promoType: 'fixed-amount',
    value: 0.5,
    startAt: '2026-02-26T00:00:00Z',
    endAt: '2026-03-01T23:59:59Z',
    priority: 2,
  },
];

const wait = async (): Promise<void> => {
  await new Promise((resolve) => setTimeout(resolve, 150));
};

export async function fetchGateways(): Promise<Gateway[]> {
  await wait();
  return gateways;
}

export async function fetchStores(): Promise<Store[]> {
  await wait();
  return stores;
}

export async function fetchShelfLocations(): Promise<ShelfLocation[]> {
  await wait();
  return shelfLocations;
}

export async function fetchProducts(): Promise<Product[]> {
  await wait();
  return products;
}

export async function fetchTags(): Promise<Tag[]> {
  await wait();
  return tags;
}

export async function fetchTagPayloads(): Promise<TagPayload[]> {
  await wait();
  return tagPayloads;
}

export async function fetchPromotions(): Promise<Promotion[]> {
  await wait();
  return promotions;
}