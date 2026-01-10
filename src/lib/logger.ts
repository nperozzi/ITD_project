import { env } from "@/env";

export default class Logger {
  constructor(private readonly context: string) {
    this.context = context;
  }

  // TODO: Implement centralized logging service
  private static logMessage(
    type: "debug" | "warning" | "info" | "error",
    context: string,
    messages: unknown[],
  ): void {
    if (type === "debug" && env.NODE_ENV === "production") {
      return;
    }

    const timestamp = new Date().toISOString();
    const level = type.toUpperCase();

    const prefix = `[${timestamp}] [${context} | ${level}]`;

    if (type === "warning") {
      console.warn(prefix, ...messages);
    } else if (type === "error") {
      console.error(prefix, ...messages);
    } else if (type === "debug") {
      // console.debug(prefix, ...messages);
    } else {
      console.log(prefix, ...messages);
    }
  }

  public warn(...messages: unknown[]): void {
    Logger.logMessage("warning", this.context, messages);
  }

  public debug(...messages: unknown[]): void {
    Logger.logMessage("debug", this.context, messages);
  }

  public error(...messages: unknown[]): void {
    Logger.logMessage("error", this.context, messages);
  }

  public info(...messages: unknown[]): void {
    Logger.logMessage("info", this.context, messages);
  }

  public static warn(context: string, ...messages: unknown[]): void {
    this.logMessage("warning", context, messages);
  }

  public static debug(context: string, ...messages: unknown[]): void {
    this.logMessage("debug", context, messages);
  }

  public static error(context: string, ...messages: unknown[]): void {
    this.logMessage("error", context, messages);
  }

  public static info(context: string, ...messages: unknown[]): void {
    this.logMessage("info", context, messages);
  }
}
