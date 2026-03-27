import type {
  Gateway,
  Product,
  Promotion,
  ShelfLocation,
  Store,
  Tag,
} from '../types';

// When VITE_BACKEND_URL is set, requests go directly to backend (for example http://localhost:5000).
// When it is empty, relative paths are used and can be handled by Vite proxy in local dev.
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL ?? '';

// Shared GET helper used by all typed read endpoints.
async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

// Shared JSON PATCH helper used by update endpoints.
async function patchJson<T>(path: string, payload: Record<string, unknown>): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Request failed for ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
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

export function fetchPromotions(): Promise<Promotion[]> {
  return fetchJson<Promotion[]>('/api/promotions');
}

export function fetchBattery(): Promise<{ battery: number | null }> {
  // Battery endpoint used by the live dashboard card.
  return fetchJson<{ battery: number | null }>('/battery');
}

export function updateProductPrice(productId: number, price: number): Promise<Product> {
  // Product price updates go through the real REST API and trigger tag payload publishing in backend.
  return patchJson<Product>(`/api/products/${productId}`, { price });
}

export function getApiBaseUrl(): string {
  // Socket.IO hook uses the same base URL as REST calls.
  return API_BASE_URL;
}
