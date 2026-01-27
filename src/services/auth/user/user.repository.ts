import "server-only";

import { db } from "@/database";
import { eq } from "drizzle-orm";
import Logger from "@/lib/logger";
import { jts } from "@/lib/utils";
import { user } from "./user.schema";

class UserRepository {
  private readonly logger = new Logger("UserRepository");

  public async createUser(params: {
    id: string;
    name: string;
    email: string;
    username?: string;
    image?: string;
  }) {
    const { id, name, email, username, image } = params;

    const [newUser] = await db
      .insert(user)
      .values({
        id,
        name,
        email,
        username,
        image,
      })
      .returning();

    this.logger.debug(`createUser(${jts(params)}) -> ${jts(newUser)}`);

    return newUser;
  }

  public async updateUser(params: {
    userId: string;
    data: { name?: string; username?: string; image?: string };
  }) {
    const { userId, data } = params;

    const [updatedUser] = await db
      .update(user)
      .set({ ...data, updatedAt: new Date() })
      .where(eq(user.id, userId))
      .returning();

    this.logger.debug(`updateUser(${jts(params)}) -> ${jts(updatedUser)}`);

    return updatedUser;
  }

  public async getUserById(params: { userId: string }) {
    const { userId } = params;

    const targetUser = await db.query.user.findFirst({
      where: eq(user.id, userId),
    });

    this.logger.debug(`getUserById(${jts(params)}) -> ${jts(targetUser)}`);

    return targetUser;
  }

  public async getUserByUsername(params: { username: string }) {
    const { username } = params;

    const targetUser = await db.query.user.findFirst({
      where: eq(user.username, username),
    });

    this.logger.debug(
      `getUserByUsername(${jts(params)}) -> ${jts(targetUser)}`,
    );

    return targetUser;
  }

  public async getUserByEmail(params: { email: string }) {
    const { email } = params;

    const targetUser = await db.query.user.findFirst({
      where: eq(user.email, email),
    });

    this.logger.debug(`getUserByEmail(${jts(params)}) -> ${jts(targetUser)}`);

    return targetUser;
  }

  public async deleteUser(params: { userId: string }) {
    const { userId } = params;

    const [deletedUser] = await db
      .delete(user)
      .where(eq(user.id, userId))
      .returning();

    this.logger.debug(`deleteUser(${jts(params)}) -> ${jts(deletedUser)}`);

    return deletedUser;
  }
}

export default UserRepository;
