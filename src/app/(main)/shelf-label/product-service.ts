import { DateFormatter } from "./date-formatter";
import { PriceCalculator } from "./price-calculator";
import { PriceFormatter } from "./price-formatter";
import type { ProductInfo } from "./types";
import { UnitConverter } from "./unit-converter";

export class ProductService {
  static getDisplayData(product: ProductInfo) {
    const effectivePrice = PriceCalculator.getEffectivePrice(product);
    const priceParts = PriceFormatter.splitPrice(
      effectivePrice,
      product.currency,
    );
    const pricePerStandardUnit =
      PriceCalculator.getPricePerStandardUnit(product);
    const isDiscountActive = PriceCalculator.isDiscountValid(product);

    return {
      name: product.name,
      brand: product.brand,
      quantity: `${product.quantity} ${UnitConverter.formatUnit(product.unit)}`,
      priceMain: priceParts.main,
      priceDecimal: priceParts.decimal,
      priceUnit: UnitConverter.formatUnit(product.unit),
      pricePerStandardUnit: pricePerStandardUnit
        ? PriceFormatter.formatPricePerUnit(
            pricePerStandardUnit,
            product.currency,
            product.unit,
          )
        : null,
      discount:
        isDiscountActive && product.discount
          ? {
              percentage: product.discount.percentage,
              validUntil: DateFormatter.format(product.discount.validUntil),
            }
          : null,
    };
  }
}
