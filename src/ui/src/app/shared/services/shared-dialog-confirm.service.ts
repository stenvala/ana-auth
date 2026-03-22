import { Injectable, inject } from "@angular/core";
import { MatDialog } from "@angular/material/dialog";
import {
  SharedConfirmDialogComponent,
  ConfirmDialogData,
} from "../components/shared-confirm-dialog/shared-confirm-dialog.component";

export type { ConfirmDialogData } from "../components/shared-confirm-dialog/shared-confirm-dialog.component";

@Injectable({
  providedIn: "root",
})
export class SharedDialogConfirmService {
  private readonly dialog = inject(MatDialog);

  async confirm(data: ConfirmDialogData): Promise<boolean> {
    return SharedConfirmDialogComponent.open(this.dialog, data);
  }

  async confirmDelete(itemName: string): Promise<boolean> {
    return await this.confirm({
      title: "Confirm deletion",
      message: `Are you sure you want to delete "${itemName}"?`,
      confirmText: "Delete",
      cancelText: "Cancel",
      confirmColor: "warn",
    });
  }

  async confirmDiscard(): Promise<boolean> {
    return await this.confirm({
      title: "Unsaved changes",
      message: "You have unsaved changes. Do you want to discard them?",
      confirmText: "Discard",
      cancelText: "Continue editing",
      confirmColor: "warn",
    });
  }
}
