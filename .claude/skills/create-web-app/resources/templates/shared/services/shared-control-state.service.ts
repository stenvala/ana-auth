import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SharedControlStateService {
  private readonly STORAGE_PREFIX = 'control_state_';

  save<T>(key: string, value: T): void {
    try {
      localStorage.setItem(this.STORAGE_PREFIX + key, JSON.stringify(value));
    } catch {
      // Ignore storage errors
    }
  }

  get<T>(key: string, defaultValue: T): T {
    try {
      const stored = localStorage.getItem(this.STORAGE_PREFIX + key);
      if (stored !== null) {
        return JSON.parse(stored) as T;
      }
    } catch {
      // Ignore parsing errors
    }
    return defaultValue;
  }

  remove(key: string): void {
    try {
      localStorage.removeItem(this.STORAGE_PREFIX + key);
    } catch {
      // Ignore storage errors
    }
  }

  clearAll(): void {
    try {
      const keysToRemove: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith(this.STORAGE_PREFIX)) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach((key) => localStorage.removeItem(key));
    } catch {
      // Ignore storage errors
    }
  }
}
