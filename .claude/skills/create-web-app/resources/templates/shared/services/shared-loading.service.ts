import { Injectable, signal, computed } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class SharedLoadingService {
  private readonly loadingCount = signal(0);

  readonly isLoading = computed(() => this.loadingCount() > 0);

  show(): void {
    this.loadingCount.update((count) => count + 1);
  }

  hide(): void {
    this.loadingCount.update((count) => Math.max(0, count - 1));
  }

  forceHide(): void {
    this.loadingCount.set(0);
  }

  async withLoading<T>(fn: () => T | Promise<T>): Promise<T> {
    this.show();
    try {
      return await fn();
    } finally {
      this.hide();
    }
  }
}
