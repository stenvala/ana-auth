import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { firstValueFrom } from 'rxjs';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmColor?: 'primary' | 'accent' | 'warn';
}

@Component({
  selector: 'app-shared-confirm-dialog',
  imports: [MatDialogModule, MatButtonModule, MatIconModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-confirm-dialog.component.html',
})
export class SharedConfirmDialogComponent {
  private readonly dialogRef = inject(MatDialogRef<SharedConfirmDialogComponent>);
  protected readonly data = inject<ConfirmDialogData>(MAT_DIALOG_DATA);

  protected onCancel(): void {
    this.dialogRef.close(false);
  }

  protected onConfirm(): void {
    this.dialogRef.close(true);
  }

  static async open(dialog: MatDialog, data: ConfirmDialogData): Promise<boolean> {
    const result = await firstValueFrom(
      dialog
        .open(SharedConfirmDialogComponent, {
          data,
          width: '400px',
          disableClose: true,
        })
        .afterClosed(),
    );
    return result === true;
  }
}
