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
  { id: 1, name: 'Downtown Market' },
  { id: 2, name: 'Riverside Market' },
];

const gateways: Gateway[] = [
  {
    id: 1,
    storeId: 1,
    status: 'online',
    lastHeartbeatAt: '2026-02-26T09:15:00Z',
  },
  {
    id: 2,
    storeId: 1,
    status: 'degraded',
    lastHeartbeatAt: '2026-02-26T09:10:00Z',
  },
  {
    id: 3,
    storeId: 2,
    status: 'offline',
    lastHeartbeatAt: '2026-02-26T08:02:00Z',
  },
];

const shelfLocations: ShelfLocation[] = [
  { id: 1, storeId: 1, aisle: 1, level: 1 },
  { id: 2, storeId: 1, aisle: 2, level: 2 },
  { id: 3, storeId: 2, aisle: 1, level: 1 },
];

const products: Product[] = [
  {
    id: 1,
    sku: 'CF-AR-1KG',
    name: 'Arabica Coffee Beans',
    attributesJson: { roast: 'medium', origin: 'Colombia', organic: true },
    price: 22.9,
  },
  {
    id: 2,
    sku: 'ML-OT-1L',
    name: 'Organic Oat Milk',
    attributesJson: { dairyFree: true, volumeMl: 1000 },
    price: 4.5,
  },
  {
    id: 3,
    sku: 'CH-DK-90G',
    name: 'Dark Chocolate Bar',
    attributesJson: { cocoaPct: 75, vegan: true },
    price: 3.2,
  },
];

const tags: Tag[] = [
  {
    id: 1,
    batteryPct: 88,
    status: 'active',
    productId: 1,
    shelfLocationId: 1,
  },
  {
    id: 2,
    batteryPct: 24,
    status: 'low-battery',
    productId: 2,
    shelfLocationId: 2,
  },
  {
    id: 3,
    batteryPct: 0,
    status: 'offline',
    productId: 3,
    shelfLocationId: 3,
  },
];

const tagPayloads: TagPayload[] = [
  {
    id: 1,
    payloadJson: { tagId: 1, title: 'Arabica Coffee Beans', price: 22.9 },
  },
  {
    id: 2,
    payloadJson: { tagId: 2, title: 'Organic Oat Milk', price: 4.5 },
  },
];

const promotions: Promotion[] = [
  {
    id: 1,
    productId: 1,
    promoType: 'percentage',
    value: 10,
    startAt: '2026-02-25T00:00:00Z',
    endAt: '2026-03-03T23:59:59Z',
    priority: 1,
  },
  {
    id: 2,
    productId: 3,
    promoType: 'percentage',
    value: 15,
    startAt: '2026-02-26T00:00:00Z',
    endAt: '2026-03-01T23:59:59Z',
    priority: 1,
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
