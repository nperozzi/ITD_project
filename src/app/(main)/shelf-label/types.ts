export type WeightUnit = "kg" | "g" | "hg";
export type VolumeUnit = "l" | "ml";
export type LengthUnit = "m" | "cm";
export type PieceUnit = "piece";

export type ProductUnit = WeightUnit | VolumeUnit | LengthUnit | PieceUnit;

export type UnitCategory = "weight" | "volume" | "length" | "piece";

export interface Currency {
  code: string;
  symbol: string;
  decimalPlaces: number;
}

export interface Discount {
  percentage: number;
  validUntil: Date;
}

export interface ProductInfo {
  name: string;
  brand: string;
  quantity: number;
  unit: ProductUnit;
  basePrice: number; // Price in smallest currency unit (e.g., cents)
  currency: Currency;
  discount?: Discount;
}
