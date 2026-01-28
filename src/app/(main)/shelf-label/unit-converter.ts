import {
  CONVERSION_TO_STANDARD,
  STANDARD_UNITS,
  UNIT_CATEGORIES,
} from "./constants";
import type { ProductUnit, UnitCategory } from "./types";

export class UnitConverter {
  static getCategory(unit: ProductUnit): UnitCategory {
    return UNIT_CATEGORIES[unit];
  }

  static getStandardUnit(unit: ProductUnit): ProductUnit {
    const category = this.getCategory(unit);
    return STANDARD_UNITS[category];
  }

  static toStandardUnit(quantity: number, unit: ProductUnit): number {
    return quantity * CONVERSION_TO_STANDARD[unit];
  }

  static formatUnit(unit: ProductUnit): string {
    return unit === "piece" ? "p" : unit;
  }

  static formatStandardUnit(unit: ProductUnit): string {
    const standardUnit = this.getStandardUnit(unit);
    return this.formatUnit(standardUnit);
  }
}
