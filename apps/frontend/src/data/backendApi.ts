import type {
  Gateway,
  Product,
  Promotion,
  ShelfLocation,
  Store,
  Tag,
  TagPayload,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL ?? '';

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

async function postForm(path: string, payload: Record<string, string>): Promise<void> {
  const body = new URLSearchParams(payload);
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body.toString(),
  });
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }
}

export function fetchStores(): Promise<Store[]> {
  return fetchJson<Store[]>('/api/stores');
}

export function fetchGateways(): Promise<Gateway[]> {
  return fetchJson<Gateway[]>('/api/gateways');
}

export function fetchShelfLocations(): Promise<ShelfLocation[]> {
  return fetchJson<ShelfLocation[]>('/api/shelf-locations');
}

export function fetchProducts(): Promise<Product[]> {
  return fetchJson<Product[]>('/api/products');
}

export function fetchTags(): Promise<Tag[]> {
  return fetchJson<Tag[]>('/api/tags');
}

export function fetchTagPayloads(): Promise<TagPayload[]> {
  return fetchJson<TagPayload[]>('/api/tag-payloads');
}

export function fetchPromotions(): Promise<Promotion[]> {
  return fetchJson<Promotion[]>('/api/promotions');
}

export function fetchBattery(): Promise<{ battery: number | null }> {
  return fetchJson<{ battery: number | null }>('/battery');
}

export function setPrice(price: string): Promise<void> {
  return postForm('/set_price', { price });
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}
