import "server-cli-only";

import type { device } from "@/database/schema";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { DeviceRepository } from "@/services/device/device.repository";

class DeviceService {
  private logger = new Logger(DeviceService.name);
  private repository = new DeviceRepository();

  async create(params: typeof device.$inferInsert) {
    try {
      const result = await this.repository.create(params);

      this.logger.debug(`create(${jts(params)}) => ${jts(result)}`);

      this.logger.info(
        `Successfully created a new device record:\n${jts(result)}`,
      );
    } catch (error) {
      this.logger.error(`Failed to create device record:\n${error}`);
    }
  }

  async read(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.read(params);

      this.logger.debug(`read(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read device record:\n${error}`);
    }
  }

  async readAll(params: { ownerId: string }) {
    try {
      const result = await this.repository.readAll(params);

      this.logger.debug(`readAll(${jts(params)}) => ${jts(result)}`);

      return result;
    } catch (error) {
      this.logger.error(`Failed to read device records:\n${error}`);
    }
  }

  async update(params: {
    id: string;
    ownerId: string;
    data: Partial<typeof device.$inferInsert>;
  }) {
    try {
      const result = await this.repository.update(params);

      this.logger.debug(`update(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully updated device record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to update device record:\n${error}`);
    }
  }

  async delete(params: { id: string; ownerId: string }) {
    try {
      const result = await this.repository.delete(params);

      this.logger.debug(`delete(${jts(params)}) => ${jts(result)}`);

      this.logger.info(`Successfully deleted device record:\n${jts(result)}`);
    } catch (error) {
      this.logger.error(`Failed to delete device record:\n${error}`);
    }
  }
}

export const deviceService = new DeviceService();
