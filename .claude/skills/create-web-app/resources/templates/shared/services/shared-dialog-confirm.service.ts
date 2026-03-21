import { Injectable, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
  SharedConfirmDialogComponent,
  ConfirmDialogData,
} from '../components/shared-confirm-dialog/shared-confirm-dialog.component';

export type { ConfirmDialogData } from '../components/shared-confirm-dialog/shared-confirm-dialog.component';

@Injectable({
  providedIn: 'root',
})
export class SharedDialogConfirmService {
  private readonly dialog = inject(MatDialog);

  async confirm(data: ConfirmDialogData): Promise<boolean> {
    return SharedConfirmDialogComponent.open(this.dialog, data);
  }

  async confirmDelete(itemName: string): Promise<boolean> {
    return await this.confirm({
      title: 'Vahvista poisto',
      message: `Haluatko varmasti poistaa kohteen "${itemName}"?`,
      confirmText: 'Poista',
      cancelText: 'Peruuta',
      confirmColor: 'warn',
    });
  }

  async confirmDiscard(): Promise<boolean> {
    return await this.confirm({
      title: 'Tallentamattomat muutokset',
      message: 'Sinulla on tallentamattomia muutoksia. Haluatko hylata muutokset?',
      confirmText: 'Hylkaa',
      cancelText: 'Jatka muokkausta',
      confirmColor: 'warn',
    });
  }
}
