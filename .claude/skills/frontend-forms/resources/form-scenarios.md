# Common Form Scenarios

## Text Input
```html
<mat-form-field appearance="outline">
  <mat-label>Name</mat-label>
  <input matInput [formField]="myForm.name" />
  @if (myForm.name().invalid() && myForm.name().touched()) {
    @for (error of myForm.name().errors(); track error.kind) {
      <mat-error>{{ error.message }}</mat-error>
    }
  }
</mat-form-field>
```

## Select Dropdown
```html
<mat-form-field appearance="outline">
  <mat-label>Category</mat-label>
  <mat-select [formField]="myForm.categoryId">
    @for (category of categories(); track category.id) {
      <mat-option [value]="category.id">{{ category.name }}</mat-option>
    }
  </mat-select>
  @if (myForm.categoryId().invalid() && myForm.categoryId().touched()) {
    @for (error of myForm.categoryId().errors(); track error.kind) {
      <mat-error>{{ error.message }}</mat-error>
    }
  }
</mat-form-field>
```

## Checkbox
```html
<mat-checkbox [formField]="myForm.isActive">Active</mat-checkbox>
```

## Date Picker
```html
<mat-form-field appearance="outline">
  <mat-label>Date</mat-label>
  <input matInput [matDatepicker]="picker" [formField]="myForm.date" />
  <mat-datepicker-toggle matIconSuffix [for]="picker"></mat-datepicker-toggle>
  <mat-datepicker #picker></mat-datepicker>
</mat-form-field>
```

## Autocomplete
```html
<mat-form-field appearance="outline">
  <mat-label>Vendor</mat-label>
  <input matInput [formField]="myForm.vendor" [matAutocomplete]="vendorAuto" />
  <mat-autocomplete #vendorAuto="matAutocomplete">
    @for (option of filteredVendors(); track option) {
      <mat-option [value]="option">{{ option }}</mat-option>
    }
  </mat-autocomplete>
</mat-form-field>
```

## Available Validators

```typescript
import { required, email, minLength, maxLength, min, max, pattern } from '@angular/forms/signals';

protected readonly myForm = form(this.formModel, (f) => {
  required(f.email, { message: 'Email is required' });
  email(f.email, { message: 'Invalid email address' });
  minLength(f.password, 8, { message: 'Password must be at least 8 characters' });
  maxLength(f.name, 100, { message: 'Name must be at most 100 characters' });
  min(f.amount, 0, { message: 'Amount must be positive' });
  max(f.amount, 1000000, { message: 'Amount is too large' });
  pattern(f.code, /^[A-Z0-9]+$/, { message: 'Code may only contain uppercase letters and numbers' });
});
```
