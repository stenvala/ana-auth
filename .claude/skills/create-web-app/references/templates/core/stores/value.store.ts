import { signal, Signal, WritableSignal } from '@angular/core';

/**
 * Simple value store using Angular signals.
 * For primitive values and simple objects.
 */
export class ValueStore<T> {
  private _value: WritableSignal<T | null>;

  readonly value: Signal<T | null>;

  constructor(initialValue: T | null = null) {
    this._value = signal(initialValue);
    this.value = this._value.asReadonly();
  }

  set(value: T): void {
    this._value.set(value);
  }

  update(fn: (current: T | null) => T | null): void {
    this._value.update(fn);
  }

  reset(initialValue: T | null = null): void {
    this._value.set(initialValue);
  }
}
