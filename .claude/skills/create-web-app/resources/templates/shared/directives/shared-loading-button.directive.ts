import { Directive, ElementRef, inject, signal, effect, input } from '@angular/core';
import { SharedConfirmService } from '../services/shared-confirm.service';

/**
 * Directive for async button operations with loading state and optional confirmation.
 *
 * Usage:
 *   <button matButton="filled" sharedLoadingButton [loadingClick]="onSave">
 *     <mat-icon>save</mat-icon>
 *     Tallenna
 *   </button>
 *
 *   <button matButton="filled" sharedLoadingButton [confirm]="true" [loadingClick]="onDelete">
 *     <mat-icon>delete</mat-icon>
 *     Poista
 *   </button>
 *
 * Component:
 *   onSave = async (): Promise<void> => {
 *     await this.service.save(this.formModel());
 *   };
 */
@Directive({
  selector: '[sharedLoadingButton]',

  host: {
    '(click)': 'onClick($event)',
  },
})
export class SharedLoadingButtonDirective {
  private readonly el = inject(ElementRef<HTMLButtonElement>);
  private readonly confirmService = inject(SharedConfirmService);

  loadingClick = input.required<() => Promise<unknown>>();
  confirm = input(false);
  confirmKey = input('');

  private readonly loading = signal(false);
  private readonly confirming = signal(false);
  private originalIconText: string | null = null;
  private originalButtonDisabled = false;

  constructor() {
    effect(() => {
      const button = this.el.nativeElement;
      const matIcon = button.querySelector('mat-icon');

      if (this.loading()) {
        if (!this.originalButtonDisabled) {
          this.originalButtonDisabled = button.disabled;
        }
        button.disabled = true;
        button.classList.add('loading');

        if (matIcon && this.originalIconText === null) {
          this.originalIconText = matIcon.textContent;
          matIcon.textContent = 'sync';
          matIcon.classList.add('spinning');
        }
      } else {
        if (!this.originalButtonDisabled) {
          button.disabled = false;
        }
        button.classList.remove('loading');

        if (matIcon && this.originalIconText !== null) {
          matIcon.textContent = this.originalIconText;
          matIcon.classList.remove('spinning');
          this.originalIconText = null;
        }
      }

      if (this.confirming()) {
        button.classList.add('confirming');
      } else {
        button.classList.remove('confirming');
      }
    });
  }

  async onClick(event: Event): Promise<void> {
    event.preventDefault();
    event.stopPropagation();

    if (this.loading()) {
      return;
    }

    if (this.confirm()) {
      const key =
        this.confirmKey() || `btn-${this.el.nativeElement.textContent?.trim() || Math.random()}`;
      if (!this.confirmService.requireConfirmation(key)) {
        this.confirming.set(true);
        setTimeout(() => this.confirming.set(false), 3000);
        return;
      }
      this.confirming.set(false);
    }

    this.loading.set(true);
    try {
      await this.loadingClick()();
    } finally {
      this.loading.set(false);
    }
  }
}
