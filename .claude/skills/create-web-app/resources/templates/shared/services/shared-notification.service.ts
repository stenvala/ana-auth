import { Injectable, inject } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

@Injectable({
  providedIn: 'root',
})
export class SharedNotificationService {
  private readonly snackBar = inject(MatSnackBar);

  private readonly defaultDuration = 4000;
  private readonly errorDuration = 6000;

  success(message: string, duration?: number): void {
    this.show(message, 'success', duration ?? this.defaultDuration);
  }

  error(message: string, duration?: number): void {
    this.show(message, 'error', duration ?? this.errorDuration);
  }

  warning(message: string, duration?: number): void {
    this.show(message, 'warning', duration ?? this.defaultDuration);
  }

  info(message: string, duration?: number): void {
    this.show(message, 'info', duration ?? this.defaultDuration);
  }

  private show(message: string, type: NotificationType, duration: number): void {
    const config: MatSnackBarConfig = {
      duration,
      horizontalPosition: 'end',
      verticalPosition: 'bottom',
      panelClass: [`snackbar-${type}`],
    };

    this.snackBar.open(message, 'Sulje', config);
  }
}
