import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Tailwind class birleştirme — shadcn bileşenleri için
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
