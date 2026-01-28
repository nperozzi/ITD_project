import "server-cli-only";

import type { gateway } from "@/database/schema";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { GatewayRepository } from "@/services/gateway/gateway.repository";
import { labelService } from "@/services/gateway/label/label.service";

class GatewayService {
  private logger = new Logger(GatewayService.name);
  private repository = new GatewayRepository();

  public label = labelService;

  async create(params: typeof gateway.$inferInsert) {
    try {
      const result = await this.repository.create(params);

      this.logger.debug(`create(${jts(params)}) => ${jts(result)}`);

      this.logger.info(
        `Successfully created a new gateway record:\n${jts(result)}`,
      );
    } catch (error) {
      this.logger.error(`Failed to create gateway record:\n${error}`);
    }
  }

  async read(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.read(params);

      this.logger.debug(`read(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read gateway record:\n${error}`);
    }
  }

  async readAll(params: { ownerId: string }) {
    try {
      const result = await this.repository.readAll(params);

      this.logger.debug(`readAll(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read gateway records:\n${error}`);
    }
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof gateway.$inferInsert>;
  }) {
    try {
      const result = await this.repository.update(params);

      this.logger.debug(`update(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully updated gateway record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to update gateway record:\n${error}`);
    }
  }

  async delete(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.delete(params);

      this.logger.debug(`delete(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully deleted gateway record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to delete gateway record:\n${error}`);
    }
  }
}

export const gatewayService = new GatewayService();
