# Dialog Component Template

## Two Dialog Patterns

There are two main patterns for dialogs:

### Pattern A: Data-Only Dialog (Simple)
- Dialog just collects data and returns it to the caller
- Host component makes the service call
- Use when: Simple forms, the caller needs to handle the result differently based on context

### Pattern B: Editor Dialog with Service Call (PREFERRED for editors)
- Dialog injects service and makes the API call itself
- If the call fails, dialog stays open so user can fix and retry
- Use when: Edit/create dialogs where you want error handling inside the dialog

---

## Pattern A: Data-Only Dialog Skeleton

Use when the host component should handle the service call.

### TypeScript Component

```typescript
import { Component, ChangeDetectionStrategy, inject, signal, effect, untracked } from '@angular/core';
import { form, FormField, required, maxLength } from '@angular/forms/signals';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { firstValueFrom } from 'rxjs';

export interface FeatureDialogItemInputData {
  // TODO: Define input fields
  isEdit: boolean;
}

export interface FeatureDialogItemOutputData {
  // TODO: Define output fields
}

interface ItemFormModel {
  // TODO: Define form fields
}

@Component({
  selector: 'feature-dialog-item',
  imports: [
    FormField,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './feature-dialog-item.component.html',
})
export class FeatureDialogItemComponent {
  private readonly dialogRef = inject(MatDialogRef<FeatureDialogItemComponent>);
  protected readonly data = inject<FeatureDialogItemInputData>(MAT_DIALOG_DATA);

  private readonly formModel = signal<ItemFormModel>({
    // TODO: Initialize form fields
  });

  protected readonly itemForm = form(this.formModel, (f) => {
    // TODO: Add validators
  });

  constructor() {
    // Initialize form with input data
    effect(() => {
      const data = this.data;
      untracked(() => {
        this.formModel.set({
          // TODO: Map input data to form model
        });
      });
    });
  }

  protected onCancel(): void {
    this.dialogRef.close();
  }

  // Pattern A: Just return data, let host handle service call
  protected onSubmit(): void {
    if (this.itemForm().valid()) {
      this.dialogRef.close(this.formModel() as FeatureDialogItemOutputData);
    }
  }

  static async open(
    dialog: MatDialog,
    data: FeatureDialogItemInputData
  ): Promise<FeatureDialogItemOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogItemComponent, {
          data,
          width: '', // TODO: Set width (e.g., '400px', '500px')
          disableClose: true,
        })
        .afterClosed()
    );
  }
}
```

### HTML Template

```html
<h2 mat-dialog-title>{{ data.isEdit ? 'Muokkaa' : 'Lisää uusi' }}</h2>

<mat-dialog-content>
  <!-- TODO: Add form fields -->
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button matButton="outlined" type="button" (click)="onCancel()">
    <mat-icon>close</mat-icon>
    Peruuta
  </button>
  <button matButton="filled" type="button" [disabled]="!itemForm().valid()" (click)="onSubmit()">
    <mat-icon>save</mat-icon>
    Tallenna
  </button>
</mat-dialog-actions>
```

---

## Pattern B: Editor Dialog with Service Call (PREFERRED)

Use this pattern when the dialog should handle the save operation itself.
If the save fails, the dialog stays open so the user can fix the issue and retry.

### TypeScript Component

```typescript
import { Component, ChangeDetectionStrategy, inject, signal, effect, untracked } from '@angular/core';
import { form, FormField, required, maxLength } from '@angular/forms/signals';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { firstValueFrom } from 'rxjs';
import { FeatureItemService } from '../../services';

export interface FeatureDialogEditItemInputData {
  itemId?: string;  // undefined = create, defined = edit
  name?: string;
  // ... other fields for edit mode
}

export interface FeatureDialogEditItemOutputData {
  success: boolean;
  itemId?: string;  // ID of created/updated item
}

interface ItemFormModel {
  name: string;
  // ... other fields
}

@Component({
  selector: 'feature-dialog-edit-item',
  imports: [
    FormField,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './feature-dialog-edit-item.component.html',
})
export class FeatureDialogEditItemComponent {
  private readonly dialogRef = inject(MatDialogRef<FeatureDialogEditItemComponent>);
  protected readonly data = inject<FeatureDialogEditItemInputData>(MAT_DIALOG_DATA);
  private readonly itemService = inject(FeatureItemService);

  protected readonly isEditMode = !!this.data.itemId;
  protected readonly isSaving = signal(false);

  private readonly formModel = signal<ItemFormModel>({
    name: this.data.name ?? '',
  });

  protected readonly itemForm = form(this.formModel, (f) => {
    required(f.name, { message: 'Nimi on pakollinen' });
    maxLength(f.name, 100, { message: 'Nimi voi olla enintään 100 merkkiä' });
  });

  protected onCancel(): void {
    this.dialogRef.close();
  }

  // Pattern B: Dialog handles the service call
  // If it fails, dialog stays open for retry
  protected onSubmit = async (): Promise<void> => {
    if (!this.itemForm().valid() || this.isSaving()) return;

    this.isSaving.set(true);
    try {
      let result;
      if (this.isEditMode) {
        result = await this.itemService.update(this.data.itemId!, {
          name: this.formModel().name,
        });
      } else {
        result = await this.itemService.create({
          name: this.formModel().name,
        });
      }

      if (result) {
        // Success - close dialog with result
        this.dialogRef.close({ success: true, itemId: result.id } as FeatureDialogEditItemOutputData);
      }
      // If result is null, service showed error notification
      // Dialog stays open for user to fix and retry
    } finally {
      this.isSaving.set(false);
    }
  };

  static async open(
    dialog: MatDialog,
    data: FeatureDialogEditItemInputData
  ): Promise<FeatureDialogEditItemOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogEditItemComponent, {
          data,
          width: '500px',
          disableClose: true,
        })
        .afterClosed()
    );
  }
}
```

### HTML Template (Pattern B)

```html
<h2 mat-dialog-title>{{ isEditMode ? 'Muokkaa' : 'Lisää uusi' }}</h2>

<mat-dialog-content>
  <mat-form-field appearance="outline" class="full-width">
    <mat-label>Nimi</mat-label>
    <input matInput [formField]="itemForm.name" />
    @if (itemForm.name().invalid() && itemForm.name().touched()) {
      @for (error of itemForm.name().errors(); track error.kind) {
        <mat-error>{{ error.message }}</mat-error>
      }
    }
  </mat-form-field>
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button matButton="outlined" type="button" (click)="onCancel()" [disabled]="isSaving()">
    <mat-icon>close</mat-icon>
    Peruuta
  </button>
  <button
    matButton="filled"
    type="button"
    [disabled]="!itemForm().valid() || isSaving()"
    sharedLoadingButton
    [loadingClick]="onSubmit"
  >
    <mat-icon>save</mat-icon>
    Tallenna
  </button>
</mat-dialog-actions>
```

---

## When to Use Which Pattern

| Pattern | Use When |
|---------|----------|
| **Pattern A (Data-Only)** | Simple data collection, caller needs to handle result differently, no complex error handling needed |
| **Pattern B (With Service)** | Edit/create operations, user should be able to retry on failure, dialog is the "owner" of the operation |

**Pattern B is preferred for most editor dialogs** because:
1. If save fails, user can fix the issue and retry without losing form data
2. Error notifications are shown while dialog is still open
3. Single responsibility - dialog handles its own persistence

---

## Simple Confirmation Dialog Pattern

Dialog for confirming an action with custom content.

**NOTE**: For confirmations, prefer using the shared `SharedDialogConfirmService` instead of creating custom confirmation dialogs.

### TypeScript Component

```typescript
import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatDialog, MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { firstValueFrom } from 'rxjs';

export interface FeatureDialogConfirmInputData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmIcon?: string;
}

export interface FeatureDialogConfirmOutputData {
  confirmed: boolean;
}

@Component({
  selector: 'feature-dialog-confirm',
  imports: [MatDialogModule, MatButtonModule, MatIconModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './feature-dialog-confirm.component.html',  // ALWAYS use separate template file
})
export class FeatureDialogConfirmComponent {
  private readonly dialogRef = inject(MatDialogRef<FeatureDialogConfirmComponent>);
  protected readonly data = inject<FeatureDialogConfirmInputData>(MAT_DIALOG_DATA);

  protected onCancel(): void {
    this.dialogRef.close();
  }

  protected onConfirm(): void {
    this.dialogRef.close({ confirmed: true } as FeatureDialogConfirmOutputData);
  }

  static async open(
    dialog: MatDialog,
    data: FeatureDialogConfirmInputData
  ): Promise<FeatureDialogConfirmOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogConfirmComponent, {
          data,
          width: '400px',
          disableClose: true,
        })
        .afterClosed()
    );
  }
}
```

### HTML Template (feature-dialog-confirm.component.html)

**IMPORTANT**: Always use a separate `.html` file for templates. Never use inline `template:` in components.

```html
<h2 mat-dialog-title>{{ data.title }}</h2>

<mat-dialog-content>
  <p>{{ data.message }}</p>
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button matButton="outlined" (click)="onCancel()">
    <mat-icon>close</mat-icon>
    {{ data.cancelText || 'Peruuta' }}
  </button>
  <button matButton="filled" (click)="onConfirm()">
    <mat-icon>{{ data.confirmIcon || 'check' }}</mat-icon>
    {{ data.confirmText || 'Vahvista' }}
  </button>
</mat-dialog-actions>
```

## Usage in Caller Component

**IMPORTANT**: Always use the static `open` method, never `dialog.open(...)` directly.

```typescript
import { Component, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { FeatureDialogItemComponent } from '../feature-dialog-item/feature-dialog-item.component';

@Component({
  // ...
})
export class RouteFeatureListComponent {
  private readonly dialog = inject(MatDialog);

  // CORRECT: Use static open method
  protected async onCreateItem(): Promise<void> {
    const result = await FeatureDialogItemComponent.open(this.dialog, {
      isEdit: false,
    });

    if (result) {
      await this.featureService.create(result);
    }
  }

  // WRONG: Never do this
  // protected async onCreateItem(): Promise<void> {
  //   const dialogRef = this.dialog.open(FeatureDialogItemComponent, { ... });
  //   const result = await firstValueFrom(dialogRef.afterClosed());
  // }
}
```

## Key Patterns Summary

### Interface Naming

```typescript
// Input: <Feature>Dialog<Name>InputData
export interface AccountingDialogEditBankAccountInputData { ... }

// Output: <Feature>Dialog<Name>OutputData
export interface AccountingDialogEditBankAccountOutputData { ... }
```

### Static Open Method Signature

```typescript
static async open(
  dialog: MatDialog,
  data: InputDataType
): Promise<OutputDataType | undefined>
```

### Handling Cancel vs Confirm

```typescript
// In caller:
const result = await MyDialogComponent.open(dialog, inputData);
if (result) {
  // User confirmed with data
} else {
  // User cancelled (result is undefined)
}
```
