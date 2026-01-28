import type { Currency, ProductUnit } from "./types";
import { UnitConverter } from "./unit-converter";

export class PriceFormatter {
  /**
   * Split price into main and decimal parts
   */
  static splitPrice(
    priceInSmallestUnit: number,
    currency: Currency,
  ): { main: string; decimal: string } {
    const divisor = Math.pow(10, currency.decimalPlaces);
    const main = Math.floor(priceInSmallestUnit / divisor);
    const decimal = priceInSmallestUnit % divisor;

    return {
      main: main.toString(),
      decimal: decimal.toString().padStart(currency.decimalPlaces, "0"),
    };
  }

  /**
   * Format price as a full string
   */
  static formatPrice(priceInSmallestUnit: number, currency: Currency): string {
    const { main, decimal } = this.splitPrice(priceInSmallestUnit, currency);
    return `${main}.${decimal}`;
  }

  /**
   * Format price per standard unit
   */
  static formatPricePerUnit(
    pricePerUnit: number,
    currency: Currency,
    unit: ProductUnit,
  ): string {
    const formattedPrice = this.formatPrice(Math.round(pricePerUnit), currency);
    const standardUnit = UnitConverter.formatStandardUnit(unit);
    return `${formattedPrice} per ${standardUnit}`;
  }
}
