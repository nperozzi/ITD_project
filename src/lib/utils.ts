import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges Tailwind class names, resolving any conflicts.
 *
 * @param inputs - An array of class names to merge.
 * @returns A string of merged and optimized class names.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Converts a value to a JSON string for logging purposes.
 * Returns "undefined" for undefined values instead of omitting them.
 *
 * @param value - The value to convert to a JSON string.
 * @returns A JSON string representation of the value.
 */
export function jts(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

/**
 * Determines the base URL of the application based on the execution environment.
 *
 * @returns The base URL as a string.
 */
export function getBaseURL(): string {
  if (typeof window !== "undefined") {
    return "";
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return `http://localhost:${process.env.PORT ?? 3000}`;
}
