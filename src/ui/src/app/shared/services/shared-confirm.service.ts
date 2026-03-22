import { Injectable, signal } from '@angular/core';

export interface ConfirmState {
  active: boolean;
  key: string;
}

@Injectable({
  providedIn: 'root',
})
export class SharedConfirmService {
  private readonly confirmState = signal<ConfirmState>({ active: false, key: '' });
  private confirmTimeout: ReturnType<typeof setTimeout> | null = null;

  readonly state = this.confirmState.asReadonly();

  isConfirming(key: string): boolean {
    const state = this.confirmState();
    return state.active && state.key === key;
  }

  requireConfirmation(key: string, timeoutMs: number = 3000): boolean {
    const state = this.confirmState();

    if (state.active && state.key === key) {
      this.reset();
      return true;
    }

    this.confirmState.set({ active: true, key });

    if (this.confirmTimeout) {
      clearTimeout(this.confirmTimeout);
    }
    this.confirmTimeout = setTimeout(() => {
      this.reset();
    }, timeoutMs);

    return false;
  }

  reset(): void {
    if (this.confirmTimeout) {
      clearTimeout(this.confirmTimeout);
      this.confirmTimeout = null;
    }
    this.confirmState.set({ active: false, key: '' });
  }
}
