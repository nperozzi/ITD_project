import { CURRENCIES } from "./constants";
import type { ProductInfo } from "./types";

export const sampleProduct: ProductInfo = {
  name: "Chicken Breast",
  brand: "Fresh Farm",
  quantity: 600,
  unit: "g",
  basePrice: 7767, // 77.67 SEK (stored in öre), will be 69.90 after 10% discount
  currency: CURRENCIES.SEK!,
  discount: {
    percentage: 10,
    validUntil: new Date("2026-12-31"),
  },
};
