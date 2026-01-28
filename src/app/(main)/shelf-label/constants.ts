import type { Currency, ProductUnit, UnitCategory } from "./types";

export const CURRENCIES: Record<string, Currency> = {
  SEK: { code: "SEK", symbol: "kr", decimalPlaces: 2 },
  EUR: { code: "EUR", symbol: "€", decimalPlaces: 2 },
  USD: { code: "USD", symbol: "$", decimalPlaces: 2 },
  GBP: { code: "GBP", symbol: "£", decimalPlaces: 2 },
};

export const UNIT_CATEGORIES: Record<ProductUnit, UnitCategory> = {
  kg: "weight",
  g: "weight",
  hg: "weight",
  l: "volume",
  ml: "volume",
  m: "length",
  cm: "length",
  piece: "piece",
};

export const STANDARD_UNITS: Record<UnitCategory, ProductUnit> = {
  weight: "kg",
  volume: "l",
  length: "m",
  piece: "piece",
};

// Conversion factors to standard unit (kg, l, m)
export const CONVERSION_TO_STANDARD: Record<ProductUnit, number> = {
  kg: 1,
  g: 0.001,
  hg: 0.1,
  l: 1,
  ml: 0.001,
  m: 1,
  cm: 0.01,
  piece: 1,
};
