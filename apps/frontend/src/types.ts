export type ConnectionStatus = 'online' | 'offline' | 'degraded';
export type TagStatus = 'active' | 'low-battery' | 'offline';

export type NavigationKey =
  | 'dashboard'
  | 'stores'
  | 'gateways'
  | 'shelf-locations'
  | 'products'
  | 'tags'
  | 'tag-payloads'
  | 'promotions';

export interface Store {
  id: string;
  name: string;
}

export interface Gateway {
  id: string;
  storeId: string;
  status: ConnectionStatus;
  lastHeartbeatAt: string;
}

export interface ShelfLocation {
  id: string;
  storeId: string;
  aisle: string;
  level: string;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  attributesJson: Record<string, string | number | boolean>;
  price: number;
}

export interface Tag {
  id: string;
  batteryPct: number;
  status: TagStatus;
  productId: string;
  shelfLocationId: string;
}

export interface TagPayload {
  id: string;
  payloadJson: Record<string, unknown>;
}

export interface Promotion {
  id: string;
  productId: string;
  promoType: 'percentage' | 'fixed-amount' | 'bundle';
  value: number;
  startAt: string;
  endAt: string;
  priority: number;
}