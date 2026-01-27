import "server-only";

import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import UserRepository from "./user.repository";

class UserService {
  private readonly logger = new Logger("UserService");
  private readonly repository: UserRepository;

  constructor() {
    this.repository = new UserRepository();
  }

  public async create(params: {
    id: string;
    name: string;
    email: string;
    username?: string;
    image?: string;
  }) {
    const result = await this.repository.createUser(params);

    if (!result) {
      const errorMessage = "Failed to create user.";
      this.logger.error(`create(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`create(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  public async update(params: {
    userId: string;
    data: { name?: string; username?: string; image?: string };
  }) {
    const result = await this.repository.updateUser(params);

    if (!result) {
      const errorMessage = "Failed to update user.";
      this.logger.error(`update(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`update(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  public async read(params: { userId: string }) {
    const result = await this.repository.getUserById(params);

    if (!result) {
      const errorMessage = `User with ID "${params.userId}" not found.`;
      this.logger.error(`read(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`read(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  public async readByUsername(params: { username: string }) {
    const result = await this.repository.getUserByUsername(params);

    if (!result) {
      const errorMessage = `User with username "${params.username}" not found.`;
      this.logger.error(`readByUsername(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`readByUsername(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  public async readByEmail(params: { email: string }) {
    const result = await this.repository.getUserByEmail(params);

    if (!result) {
      const errorMessage = `User with email "${params.email}" not found.`;
      this.logger.error(`readByEmail(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`readByEmail(${jts(params)}) -> ${jts(result)}`);
    return result;
  }

  public async delete(params: { userId: string }) {
    const result = await this.repository.deleteUser(params);

    if (!result) {
      const errorMessage = "Failed to delete user.";
      this.logger.error(`delete(${jts(params)}): ${errorMessage}`);
      throw new Error(errorMessage);
    }

    this.logger.debug(`delete(${jts(params)}) -> ${jts(result)}`);
    return result;
  }
}

export const userService = new UserService();
