import "server-cli-only";

import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { ProductRepository } from "@/services/product/product.repository";
import type { ProductPriceDetails } from "@/services/product/product.schema";

/**
 * Product Service - Business logic for product management.
 * Handles CRUD operations for products that can be assigned to labels.
 */
class ProductService {
  private readonly logger = new Logger("ProductService");
  private readonly repository = new ProductRepository();

  /**
   * Create a new product.
   */
  async create(params: {
    ownerId: string;
    name: string;
    brand?: string;
    barcode?: string;
    sku?: string;
    description?: string;
    priceDetails: ProductPriceDetails;
  }) {
    // Check for duplicate barcode if provided
    if (params.barcode) {
      const existing = await this.repository.readByBarcode({
        barcode: params.barcode,
        ownerId: params.ownerId,
      });

      if (existing) {
        const errorMessage = `Product with barcode "${params.barcode}" already exists.`;
        this.logger.error(`create(${jts(params)}): ${errorMessage}`);
        throw new Error(errorMessage);
      }
    }

    const result = await this.repository.create({
      ownerId: params.ownerId,
      name: params.name,
      brand: params.brand,
      barcode: params.barcode,
      sku: params.sku,
      description: params.description,
      priceDetails: params.priceDetails,
    });

    this.logger.debug(`create(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get a specific product by ID.
   */
  async read(params: { id: string; ownerId: string }) {
    const result = await this.repository.read(params);

    if (!result) {
      const errorMessage = `Product with ID "${params.id}" not found.`;
      this.logger.error(`read(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`read(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Get all products for a user.
   */
  async readAll(params: { ownerId: string }) {
    const result = await this.repository.readAll(params);
    this.logger.debug(`readAll(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Get all active products for a user.
   */
  async readActive(params: { ownerId: string }) {
    const result = await this.repository.readActive(params);
    this.logger.debug(`readActive(${jts(params)}) -> ${result.length} records`);
    return result;
  }

  /**
   * Update a product.
   */
  async update(params: {
    id: string;
    ownerId: string;
    name?: string;
    brand?: string | null;
    barcode?: string | null;
    sku?: string | null;
    description?: string | null;
    priceDetails?: ProductPriceDetails;
    isActive?: boolean;
  }) {
    // Check for duplicate barcode if changing it
    if (params.barcode) {
      const existing = await this.repository.readByBarcode({
        barcode: params.barcode,
        ownerId: params.ownerId,
      });

      if (existing && existing.id !== params.id) {
        const errorMessage = `Product with barcode "${params.barcode}" already exists.`;
        this.logger.error(`update(${jts(params)}): ${errorMessage}`);
        throw new Error(errorMessage);
      }
    }

    const result = await this.repository.update({
      id: params.id,
      ownerId: params.ownerId,
      data: {
        name: params.name,
        brand: params.brand,
        barcode: params.barcode,
        sku: params.sku,
        description: params.description,
        priceDetails: params.priceDetails,
        isActive: params.isActive,
      },
    });

    if (!result) {
      const errorMessage = `Product with ID "${params.id}" not found.`;
      this.logger.error(`update(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`update(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  /**
   * Delete a product.
   */
  async delete(params: { id: string; ownerId: string }) {
    const result = await this.repository.delete(params);

    if (!result) {
      const errorMessage = `Product with ID "${params.id}" not found.`;
      this.logger.error(`delete(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`delete(${jts(params)}) -> ${jts(result)}`);
    return result;
  }
}

export const productService = new ProductService();
