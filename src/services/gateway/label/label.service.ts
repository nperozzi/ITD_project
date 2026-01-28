import "server-cli-only";

import type { label } from "@/database/schema";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { LabelRepository } from "@/services/gateway/label/label.repository";

class LabelService {
  private logger = new Logger(LabelService.name);
  private repository = new LabelRepository();

  async create(params: typeof label.$inferInsert) {
    try {
      const result = await this.repository.create(params);

      this.logger.debug(`create(${jts(params)}) => ${jts(result)}`);

      this.logger.info(
        `Successfully created a new label record:\n${jts(result)}`,
      );
    } catch (error) {
      this.logger.error(`Failed to create label record:\n${error}`);
    }
  }

  async read(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.read(params);

      this.logger.debug(`read(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read label record:\n${error}`);
    }
  }

  async readAll(params: { ownerId: string }) {
    try {
      const result = await this.repository.readAll(params);

      this.logger.debug(`readAll(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read label records:\n${error}`);
    }
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof label.$inferInsert>;
  }) {
    try {
      const result = await this.repository.update(params);

      this.logger.debug(`update(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully updated label record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to update label record:\n${error}`);
    }
  }

  async delete(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.delete(params);

      this.logger.debug(`delete(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully deleted label record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to delete label record:\n${error}`);
    }
  }
}

export const labelService = new LabelService();
