# Signal Form Dialog Template (Pattern 1)

## Simple Dialog Form Pattern

Dialog with form for creating/editing data using Angular 21 signal-based forms.

### TypeScript Component

```typescript
import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { form, FormField, required, maxLength } from '@angular/forms/signals';
import { MatDialog, MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { firstValueFrom } from 'rxjs';
import { SharedLoadingButtonDirective } from '@shared/directives/shared-loading-button.directive';

/**
 * Input data for the dialog
 */
export interface FeatureDialogItemInputData {
  /** Existing item data for edit mode, undefined for create mode */
  item?: {
    id: string;
    name: string;
  };
}

/**
 * Output data when dialog is confirmed
 */
export interface FeatureDialogItemOutputData {
  name: string;
}

/**
 * Form model interface
 */
interface ItemFormModel {
  name: string;
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
    SharedLoadingButtonDirective,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './feature-dialog-item.component.html',
})
export class FeatureDialogItemComponent {
  private readonly dialogRef = inject(MatDialogRef<FeatureDialogItemComponent>);
  protected readonly data = inject<FeatureDialogItemInputData>(MAT_DIALOG_DATA);

  protected readonly isEditMode = !!this.data.item;
  protected readonly dialogTitle = this.isEditMode ? 'Muokkaa' : 'Luo uusi';

  // Form model as signal
  private readonly formModel = signal<ItemFormModel>({
    name: this.data.item?.name ?? '',
  });

  // Field tree with validation
  protected readonly itemForm = form(this.formModel, (f) => {
    required(f.name, { message: 'Nimi on pakollinen' });
    maxLength(f.name, 100, { message: 'Nimi voi olla enintään 100 merkkiä' });
  });

  protected onCancel(): void {
    this.dialogRef.close();
  }

  protected onSubmit(): void {
    if (this.itemForm().valid()) {
      this.dialogRef.close(this.formModel() as FeatureDialogItemOutputData);
    }
  }

  /**
   * Static method to open the dialog
   */
  static async open(
    dialog: MatDialog,
    data: FeatureDialogItemInputData
  ): Promise<FeatureDialogItemOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogItemComponent, {
          data,
          width: '500px',
          disableClose: false,
        })
        .afterClosed()
    );
  }
}
```

### HTML Template

```html
<h2 mat-dialog-title>{{ dialogTitle }}</h2>

<mat-dialog-content>
  <mat-form-field appearance="outline" class="full-width">
    <mat-label>Nimi</mat-label>
    <input matInput [formField]="itemForm.name" data-test-id="input-name" />
    @if (itemForm.name().invalid() && itemForm.name().touched()) {
      @for (error of itemForm.name().errors(); track error.kind) {
        <mat-error>{{ error.message }}</mat-error>
      }
    }
  </mat-form-field>
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button matButton="outlined" type="button" (click)="onCancel()" data-test-id="btn-cancel">
    <mat-icon>close</mat-icon>
    Peruuta
  </button>
  <button matButton="filled"
          sharedLoadingButton
          [disabled]="!itemForm().valid()"
          (loadingClick)="onSubmit()"
          data-test-id="btn-submit">
    <mat-icon>save</mat-icon>
    {{ isEditMode ? 'Päivitä' : 'Luo' }}
  </button>
</mat-dialog-actions>
```

## Multi-Field Dialog Form (Pattern 2)

Dialog with multiple form fields including select dropdown.

### TypeScript Component

```typescript
import { Component, ChangeDetectionStrategy, inject, signal } from '@angular/core';
import { form, FormField, required, maxLength } from '@angular/forms/signals';
import { MatDialog, MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { firstValueFrom } from 'rxjs';
import { SharedLoadingButtonDirective } from '@shared/directives/shared-loading-button.directive';

export interface FeatureDialogComplexInputData {
  item?: {
    id: string;
    code: string;
    name: string;
    categoryId: string;
  };
  categories: { id: string; name: string }[];
}

export interface FeatureDialogComplexOutputData {
  code: string;
  name: string;
  categoryId: string;
}

interface ComplexFormModel {
  code: string;
  name: string;
  categoryId: string;
}

@Component({
  selector: 'feature-dialog-complex',
  imports: [
    FormField,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    SharedLoadingButtonDirective,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './feature-dialog-complex.component.html',
})
export class FeatureDialogComplexComponent {
  private readonly dialogRef = inject(MatDialogRef<FeatureDialogComplexComponent>);
  protected readonly data = inject<FeatureDialogComplexInputData>(MAT_DIALOG_DATA);

  protected readonly isEditMode = !!this.data.item;

  private readonly formModel = signal<ComplexFormModel>({
    code: this.data.item?.code ?? '',
    name: this.data.item?.name ?? '',
    categoryId: this.data.item?.categoryId ?? '',
  });

  protected readonly complexForm = form(this.formModel, (f) => {
    required(f.code, { message: 'Koodi on pakollinen' });
    maxLength(f.code, 20, { message: 'Koodi voi olla enintään 20 merkkiä' });
    required(f.name, { message: 'Nimi on pakollinen' });
    maxLength(f.name, 100, { message: 'Nimi voi olla enintään 100 merkkiä' });
    required(f.categoryId, { message: 'Kategoria on pakollinen' });
  });

  protected onCancel(): void {
    this.dialogRef.close();
  }

  protected onSubmit(): void {
    if (this.complexForm().valid()) {
      this.dialogRef.close(this.formModel() as FeatureDialogComplexOutputData);
    }
  }

  static async open(
    dialog: MatDialog,
    data: FeatureDialogComplexInputData
  ): Promise<FeatureDialogComplexOutputData | undefined> {
    return await firstValueFrom(
      dialog
        .open(FeatureDialogComplexComponent, {
          data,
          width: '500px',
          disableClose: false,
        })
        .afterClosed()
    );
  }
}
```

### HTML Template

```html
<h2 mat-dialog-title>{{ isEditMode ? 'Muokkaa' : 'Luo uusi' }}</h2>

<mat-dialog-content>
  <mat-form-field appearance="outline" class="full-width">
    <mat-label>Koodi</mat-label>
    <input matInput [formField]="complexForm.code" data-test-id="input-code" />
    @if (complexForm.code().invalid() && complexForm.code().touched()) {
      @for (error of complexForm.code().errors(); track error.kind) {
        <mat-error>{{ error.message }}</mat-error>
      }
    }
  </mat-form-field>

  <mat-form-field appearance="outline" class="full-width">
    <mat-label>Nimi</mat-label>
    <input matInput [formField]="complexForm.name" data-test-id="input-name" />
    @if (complexForm.name().invalid() && complexForm.name().touched()) {
      @for (error of complexForm.name().errors(); track error.kind) {
        <mat-error>{{ error.message }}</mat-error>
      }
    }
  </mat-form-field>

  <mat-form-field appearance="outline" class="full-width">
    <mat-label>Kategoria</mat-label>
    <mat-select [formField]="complexForm.categoryId" data-test-id="select-category">
      @for (category of data.categories; track category.id) {
        <mat-option [value]="category.id">{{ category.name }}</mat-option>
      }
    </mat-select>
    @if (complexForm.categoryId().invalid() && complexForm.categoryId().touched()) {
      @for (error of complexForm.categoryId().errors(); track error.kind) {
        <mat-error>{{ error.message }}</mat-error>
      }
    }
  </mat-form-field>
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button matButton="outlined" type="button" (click)="onCancel()" data-test-id="btn-cancel">
    <mat-icon>close</mat-icon>
    Peruuta
  </button>
  <button matButton="filled"
          sharedLoadingButton
          [disabled]="!complexForm().valid()"
          (loadingClick)="onSubmit()"
          data-test-id="btn-submit">
    <mat-icon>save</mat-icon>
    {{ isEditMode ? 'Päivitä' : 'Luo' }}
  </button>
</mat-dialog-actions>
```

## Key Differences from ReactiveFormsModule

| Aspect | ReactiveFormsModule | Signal Forms |
|--------|---------------------|--------------|
| Form creation | `this.fb.group({...})` | `signal<T>({...})` + `form(signal)` |
| Field binding | `formControlName="name"` | `[formField]="myForm.name"` |
| Validity check | `this.form.valid` | `this.myForm().valid()` |
| Getting values | `this.form.getRawValue()` | `this.formModel()` |
| Error display | `form.controls.name.hasError('required')` | `myForm.name().errors()` |
| Submit disabled | `[disabled]="form.invalid"` | `[disabled]="!myForm().valid()"` |
