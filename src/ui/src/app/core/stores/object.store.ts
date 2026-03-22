import { Signal, signal, WritableSignal } from '@angular/core';

export class ObjectStore<T> {
  private data: Record<string, WritableSignal<T | null>> = {};

  has(key: string): boolean {
    return !!this.data[key];
  }

  isInitialized(key: string): boolean {
    return !!(this.data[key] && this.data[key]!());
  }

  get(key: string): Signal<T | null> {
    if (!this.data[key]) {
      this.data[key] = signal<T | null>(null);
    }
    return this.data[key].asReadonly();
  }

  set(key: string, value: T) {
    if (!this.data[key]) {
      this.data[key] = signal<T | null>(value);
    } else {
      this.data[key]!.set(value);
    }
  }

  remove(key: string) {
    delete this.data[key];
  }

  clear() {
    this.data = {};
  }

  nullify(key: string) {
    if (this.data[key]) {
      this.data[key]!.set(null);
    }
  }

  getInitializedKeys(): string[] {
    return Object.keys(this.data).filter((key) => this.isInitialized(key));
  }
}
