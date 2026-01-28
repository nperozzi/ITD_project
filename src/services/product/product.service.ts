import "server-cli-only";

import type { product } from "@/database/schema";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { ProductRepository } from "@/services/product/product.repository";

class ProductService {
  private logger = new Logger(ProductService.name);
  private repository = new ProductRepository();

  async create(params: typeof product.$inferInsert) {
    try {
      const result = await this.repository.create(params);

      this.logger.debug(`create(${jts(params)}) => ${jts(result)}`);

      this.logger.info(
        `Successfully created a new product record:\n${jts(result)}`,
      );
    } catch (error) {
      this.logger.error(`Failed to create product record:\n${error}`);
    }
  }

  async read(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.read(params);

      this.logger.debug(`read(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read product record:\n${error}`);
    }
  }

  async readAll(params: { ownerId: string }) {
    try {
      const result = await this.repository.readAll(params);

      this.logger.debug(`readAll(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read product records:\n${error}`);
    }
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof product.$inferInsert>;
  }) {
    try {
      const result = await this.repository.update(params);

      this.logger.debug(`update(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully updated product record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to update product record:\n${error}`);
    }
  }

  async delete(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.delete(params);

      this.logger.debug(`delete(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully deleted product record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to delete product record:\n${error}`);
    }
  }
}

export const productService = new ProductService();
