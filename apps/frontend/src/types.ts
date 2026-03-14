export type ConnectionStatus = 'online' | 'offline' | 'degraded';
export type TagStatus = 'active' | 'low-battery' | 'offline';
export type EntityId = number;

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
  id: EntityId;
  name: string;
}

export interface Gateway {
  id: EntityId;
  storeId: EntityId | null;
  status: ConnectionStatus;
  lastHeartbeatAt: string;
}

export interface ShelfLocation {
  id: EntityId;
  storeId: EntityId;
  aisle: number;
  level: number;
}

export interface Product {
  id: EntityId;
  sku: string;
  name: string;
  attributesJson: Record<string, string | number | boolean>;
  price: number;
}

export interface Tag {
  id: EntityId;
  batteryPct: number;
  status: TagStatus;
  productId: EntityId | null;
  shelfLocationId: EntityId | null;
}

export interface TagPayload {
  id: EntityId;
  payloadJson: Record<string, unknown>;
}

export interface Promotion {
  id: EntityId;
  productId: EntityId | null;
  promoType: 'percentage';
  value: number;
  startAt: string;
  endAt: string;
  priority: number;
}
