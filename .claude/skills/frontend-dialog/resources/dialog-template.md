# Dialog Component Template

## Two Dialog Patterns

There are two main patterns for dialogs:

### Pattern A: Data-Only Dialog (Simple)

- Dialog just collects data and returns it to the caller
- Host component makes the service call
- Use when: Simple forms, the caller needs to handle the result differently based on context

### Pattern B: Editor Dialog with Service Call (PREFERRED)

- Dialog injects service and makes the API call itself
- If the call fails, dialog stays open so user can fix and retry
- Use when: Edit/create dialogs where you want error handling inside the dialog

---

## Pattern A: Data-Only Dialog Skeleton

Use when the host component should handle the service call.

### TypeScript Component

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
} from "@angular/core";
import { form, FormField, required, maxLength } from "@angular/forms/signals";
import {
  MAT_DIALOG_DATA,
  MatDialogRef,
  MatDialog,
} from "@angular/material/dialog";
import { firstValueFrom } from "rxjs";
import { CoreModule } from "@core/core.module";
import { MaterialModule } from "@shared/material";
import { SharedModule } from "@shared/shared.module";

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
  selector: "feature-dialog-item",
  imports: [CoreModule, MaterialModule, SharedModule, FormField],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: "./feature-dialog-item.component.html",
})
export class FeatureDialogItemComponent {
  private readonly dialogRef = inject(MatDialogRef<FeatureDialogItemComponent>);
  protected readonly data =
    inject<FeatureDialogItemInputData>(MAT_DIALOG_DATA);

  private readonly formModel = signal<ItemFormModel>({
    // TODO: Initialize form fields
  });

  protected readonly itemForm = form(this.formModel, (f) => {
    // TODO: Add validators
  });

  protected onCancel(): void {
    this.dialogRef.close();
  }

  // Pattern A: Just return data, let host handle service call
  protected onSubmit(): void {
    if (this.itemForm().valid()) {
      this.dialogRef.close(
        this.formModel() as FeatureDialogItemOutputData,
      );
    }
  }

  static async open(
    dialog: MatDialog,
    data: FeatureDialogItemInputData,
  ): Promise<FeatureDialogItemOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogItemComponent, {
          data,
          width: "", // TODO: Set width (e.g., '400px', '500px')
          disableClose: true,
        })
        .afterClosed(),
    );
  }
}
```

### HTML Template

```html
<h2 mat-dialog-title>{{ data.isEdit ? 'Edit' : 'Create' }}</h2>

<mat-dialog-content>
  <!-- TODO: Add form fields -->
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button
    matButton
    class="btn-cancel"
    type="button"
    (click)="onCancel()"
    data-test-id="btn-cancel"
  >
    <mat-icon>close</mat-icon>
    Cancel
  </button>
  <button
    matButton
    class="btn-action"
    type="button"
    [disabled]="!itemForm().valid()"
    (click)="onSubmit()"
    data-test-id="btn-submit"
  >
    <mat-icon>save</mat-icon>
    Save
  </button>
</mat-dialog-actions>
```

---

## Pattern B: Editor Dialog with Service Call (PREFERRED)

Use this pattern when the dialog should handle the save operation itself.
If the save fails, the dialog stays open so the user can fix the issue and retry.

### TypeScript Component

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
} from "@angular/core";
import { form, FormField, required, maxLength } from "@angular/forms/signals";
import {
  MAT_DIALOG_DATA,
  MatDialogRef,
  MatDialog,
} from "@angular/material/dialog";
import { firstValueFrom } from "rxjs";
import { CoreModule } from "@core/core.module";
import { MaterialModule } from "@shared/material";
import { SharedModule } from "@shared/shared.module";
import { SharedNotificationService } from "@shared/services";
import { FeatureItemService } from "../../services";

export interface FeatureDialogItemInputData {
  itemId?: string; // undefined = create, defined = edit
  name?: string;
  // ... other fields for edit mode
}

export interface FeatureDialogItemOutputData {
  success: boolean;
}

interface ItemFormModel {
  name: string;
  // ... other fields
}

@Component({
  selector: "feature-dialog-item",
  imports: [CoreModule, MaterialModule, SharedModule, FormField],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: "./feature-dialog-item.component.html",
})
export class FeatureDialogItemComponent {
  private readonly dialogRef = inject(
    MatDialogRef<FeatureDialogItemComponent>,
  );
  protected readonly data =
    inject<FeatureDialogItemInputData>(MAT_DIALOG_DATA);
  private readonly itemService = inject(FeatureItemService);
  private readonly notification = inject(SharedNotificationService);

  protected readonly isEditMode = !!this.data.itemId;

  private readonly formModel = signal<ItemFormModel>({
    name: this.data.name ?? "",
  });

  protected readonly itemForm = form(this.formModel, (f) => {
    required(f.name, { message: "Name is required" });
    maxLength(f.name, 100, {
      message: "Name must be at most 100 characters",
    });
  });

  protected onCancel(): void {
    this.dialogRef.close();
  }

  // Pattern B: Arrow function for sharedLoadingButton directive
  // If save fails, dialog stays open for retry
  protected onSubmit = async (): Promise<void> => {
    if (!this.itemForm().valid()) return;

    try {
      if (this.isEditMode) {
        await this.itemService.update(this.data.itemId!, {
          name: this.formModel().name,
        });
      } else {
        await this.itemService.create({
          name: this.formModel().name,
        });
      }
      this.notification.success(
        this.isEditMode ? "Updated successfully" : "Created successfully",
      );
      this.dialogRef.close({ success: true } as FeatureDialogItemOutputData);
    } catch {
      this.notification.error(
        this.isEditMode ? "Failed to update" : "Failed to create",
      );
    }
  };

  static async open(
    dialog: MatDialog,
    data: FeatureDialogItemInputData,
  ): Promise<FeatureDialogItemOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogItemComponent, {
          data,
          width: "500px",
          disableClose: true,
        })
        .afterClosed(),
    );
  }
}
```

### HTML Template (Pattern B)

```html
<h2 mat-dialog-title>{{ isEditMode ? 'Edit' : 'Create' }}</h2>

<mat-dialog-content>
  <mat-form-field appearance="outline" class="full-width">
    <mat-label>Name</mat-label>
    <input matInput [formField]="itemForm.name" data-test-id="input-name" />
    @if (itemForm.name().invalid() && itemForm.name().touched()) {
      @for (error of itemForm.name().errors(); track error.kind) {
        <mat-error>{{ error.message }}</mat-error>
      }
    }
  </mat-form-field>
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button
    matButton
    class="btn-cancel"
    type="button"
    (click)="onCancel()"
    data-test-id="btn-cancel"
  >
    <mat-icon>close</mat-icon>
    Cancel
  </button>
  <button
    matButton
    class="btn-action"
    type="button"
    sharedLoadingButton
    [disabled]="!itemForm().valid()"
    [loadingClick]="onSubmit"
    data-test-id="btn-submit"
  >
    <mat-icon>save</mat-icon>
    Save
  </button>
</mat-dialog-actions>
```

---

## When to Use Which Pattern

| Pattern                      | Use When                                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Pattern A (Data-Only)**    | Simple data collection, caller needs to handle result differently, no complex error handling needed      |
| **Pattern B (With Service)** | Edit/create operations, user should be able to retry on failure, dialog is the "owner" of the operation  |

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
import { Component, ChangeDetectionStrategy, inject } from "@angular/core";
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogRef,
} from "@angular/material/dialog";
import { firstValueFrom } from "rxjs";
import { CoreModule } from "@core/core.module";
import { MaterialModule } from "@shared/material";
import { SharedModule } from "@shared/shared.module";

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
  selector: "feature-dialog-confirm",
  imports: [CoreModule, MaterialModule, SharedModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: "./feature-dialog-confirm.component.html",
})
export class FeatureDialogConfirmComponent {
  private readonly dialogRef = inject(
    MatDialogRef<FeatureDialogConfirmComponent>,
  );
  protected readonly data =
    inject<FeatureDialogConfirmInputData>(MAT_DIALOG_DATA);

  protected onCancel(): void {
    this.dialogRef.close();
  }

  protected onConfirm(): void {
    this.dialogRef.close({
      confirmed: true,
    } as FeatureDialogConfirmOutputData);
  }

  static async open(
    dialog: MatDialog,
    data: FeatureDialogConfirmInputData,
  ): Promise<FeatureDialogConfirmOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogConfirmComponent, {
          data,
          width: "400px",
          disableClose: true,
        })
        .afterClosed(),
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
  <button matButton class="btn-cancel" (click)="onCancel()" data-test-id="btn-cancel">
    <mat-icon>close</mat-icon>
    {{ data.cancelText || 'Cancel' }}
  </button>
  <button matButton class="btn-action" (click)="onConfirm()" data-test-id="btn-confirm">
    <mat-icon>{{ data.confirmIcon || 'check' }}</mat-icon>
    {{ data.confirmText || 'Confirm' }}
  </button>
</mat-dialog-actions>
```

## Usage in Caller Component

**IMPORTANT**: Always use the static `open` method, never `dialog.open(...)` directly.

```typescript
import { Component, inject } from "@angular/core";
import { MatDialog } from "@angular/material/dialog";
import { FeatureDialogItemComponent } from "../feature-dialog-item/feature-dialog-item.component";

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
      // Pattern A: host handles the result
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

---

## Scaffold Template

This section is used by `scripts/init_frontend_dialog.py` to generate new dialog components.

**Tokens:** `__FEATURE__` (PascalCase), `__feature__` (kebab), `__NAME__` (PascalCase), `__name__` (kebab), `__FORM__` (camelCase form name).

### TypeScript Scaffold

<!-- scaffold:ts -->
```typescript
import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
} from '@angular/core';
import { form, FormField, required, maxLength } from '@angular/forms/signals';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialog } from '@angular/material/dialog';
import { firstValueFrom } from 'rxjs';
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/material';
import { SharedModule } from '@shared/shared.module';

export interface __FEATURE__Dialog__NAME__InputData {
  // TODO: Define input fields
  isEdit: boolean;
}

export interface __FEATURE__Dialog__NAME__OutputData {
  // TODO: Define output fields
}

interface __NAME__FormModel {
  // TODO: Define form fields
}

@Component({
  selector: '__feature__-dialog-__name__',
  imports: [CoreModule, MaterialModule, SharedModule, FormField],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './__feature__-dialog-__name__.component.html',
})
export class __FEATURE__Dialog__NAME__Component {
  private readonly dialogRef = inject(MatDialogRef<__FEATURE__Dialog__NAME__Component>);
  protected readonly data = inject<__FEATURE__Dialog__NAME__InputData>(MAT_DIALOG_DATA);
  // TODO: Inject your feature service
  // private readonly service = inject(YourService);
  // private readonly notification = inject(SharedNotificationService);

  protected readonly isEditMode = !!this.data.isEdit;

  private readonly formModel = signal<__NAME__FormModel>({
    // TODO: Initialize form fields
  });

  protected readonly __FORM__Form = form(this.formModel, (f) => {
    // TODO: Add validators
  });

  protected onCancel(): void {
    this.dialogRef.close();
  }

  // Pattern B: Arrow function for sharedLoadingButton directive
  protected onSubmit = async (): Promise<void> => {
    if (!this.__FORM__Form().valid()) return;

    // TODO: Implement save logic (Pattern B)
    // try {
    //   await this.service.save(this.formModel());
    //   this.notification.success('Saved successfully');
    //   this.dialogRef.close({ /* output data */ } as __FEATURE__Dialog__NAME__OutputData);
    // } catch {
    //   this.notification.error('Failed to save');
    // }
  };

  static async open(
    dialog: MatDialog,
    data: __FEATURE__Dialog__NAME__InputData,
  ): Promise<__FEATURE__Dialog__NAME__OutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(__FEATURE__Dialog__NAME__Component, {
          data,
          width: '500px',
          disableClose: true,
        })
        .afterClosed(),
    );
  }
}
```

### HTML Scaffold

<!-- scaffold:html -->
```html
<h2 mat-dialog-title>{{ isEditMode ? 'Edit' : 'Create' }}</h2>

<mat-dialog-content>
  <!-- TODO: Add form fields -->
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button
    matButton
    class="btn-cancel"
    type="button"
    (click)="onCancel()"
    data-test-id="btn-cancel"
  >
    <mat-icon>close</mat-icon>
    Cancel
  </button>
  <button
    matButton
    class="btn-action"
    type="button"
    sharedLoadingButton
    [disabled]="!__FORM__Form().valid()"
    [loadingClick]="onSubmit"
    data-test-id="btn-submit"
  >
    <mat-icon>save</mat-icon>
    Save
  </button>
</mat-dialog-actions>
```
