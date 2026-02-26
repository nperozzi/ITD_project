import useSWR from 'swr';
import {
  fetchGateways,
  fetchPromotions,
  fetchProducts,
  fetchShelfLocations,
  fetchStores,
  fetchTagPayloads,
  fetchTags,
} from '../data/backendApi';

// These small wrappers keep component code simple and provide SWR caching per resource key.
export function useStores() {
  return useSWR('stores', fetchStores);
}

export function useGateways() {
  return useSWR('gateways', fetchGateways);
}

export function useShelfLocations() {
  return useSWR('shelf-locations', fetchShelfLocations);
}

export function useProducts() {
  return useSWR('products', fetchProducts);
}

export function useTags() {
  return useSWR('tags', fetchTags);
}

export function useTagPayloads() {
  return useSWR('tag-payloads', fetchTagPayloads);
}

export function usePromotions() {
  return useSWR('promotions', fetchPromotions);
}
