import type { ProductInfo } from "./types";
import { UnitConverter } from "./unit-converter";

export class PriceCalculator {
  /**
   * Calculate the effective price after discount
   */
  static getEffectivePrice(product: ProductInfo): number {
    if (!product.discount) return product.basePrice;

    const discountMultiplier = 1 - product.discount.percentage / 100;
    return Math.round(product.basePrice * discountMultiplier);
  }

  /**
   * Calculate price per standard unit (per kg, per l, per m)
   */
  static getPricePerStandardUnit(product: ProductInfo): number | null {
    const category = UnitConverter.getCategory(product.unit);

    // No per-unit price for items sold by piece
    if (category === "piece") return null;

    const standardQuantity = UnitConverter.toStandardUnit(
      product.quantity,
      product.unit,
    );

    const effectivePrice = this.getEffectivePrice(product);
    return effectivePrice / standardQuantity;
  }

  /**
   * Check if discount is currently valid
   */
  static isDiscountValid(product: ProductInfo): boolean {
    if (!product.discount) return false;
    return product.discount.validUntil >= new Date();
  }
}
