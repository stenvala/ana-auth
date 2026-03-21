# Signal Form Patterns Reference

## Validation Patterns

### Available Validators

```typescript
import { required, email, minLength, maxLength, min, max, pattern } from '@angular/forms/signals';

protected readonly myForm = form(this.formModel, (f) => {
  // Required field
  required(f.name, { message: 'Nimi on pakollinen' });

  // Email validation
  email(f.email, { message: 'Virheellinen sähköpostiosoite' });

  // Length constraints
  minLength(f.password, 8, { message: 'Salasanan on oltava vähintään 8 merkkiä' });
  maxLength(f.name, 100, { message: 'Nimi voi olla enintään 100 merkkiä' });

  // Numeric constraints
  min(f.amount, 0, { message: 'Summan on oltava positiivinen' });
  max(f.amount, 1000000, { message: 'Summa on liian suuri' });

  // Pattern matching
  pattern(f.code, /^[A-Z0-9]+$/, { message: 'Koodi saa sisältää vain isoja kirjaimia ja numeroita' });
});
```

### Error Display Pattern

```html
<mat-form-field appearance="outline">
  <mat-label>Sähköposti</mat-label>
  <input matInput [formField]="myForm.email" />
  @if (myForm.email().invalid() && myForm.email().touched()) {
    @for (error of myForm.email().errors(); track error.kind) {
      <mat-error>{{ error.message }}</mat-error>
    }
  }
</mat-form-field>
```

### Multiple Validators on Same Field

```typescript
protected readonly myForm = form(this.formModel, (f) => {
  // Chain multiple validators
  required(f.email, { message: 'Sähköposti on pakollinen' });
  email(f.email, { message: 'Virheellinen sähköpostiosoite' });
  maxLength(f.email, 255, { message: 'Sähköposti on liian pitkä' });
});
```

---

## Button Styling Rules (Pattern 7)

### Button Variant Mapping

| Button Purpose | Variant | Example |
|---------------|---------|---------|
| Primary action (save, confirm, search, fetch) | `matButton="filled"` | Save, Submit, Search |
| Cancel/dismiss action | `matButton="outlined"` | Cancel, Close, Dismiss |
| Navigation/open dialog to add something | `matButton="elevated"` | Add New, Create, Open |

### CRITICAL: Icon Requirements

**ALL buttons MUST have either icon-only OR icon with text. Text-only buttons are PROHIBITED.**

### Button with Icon and Text

```html
<!-- Primary action -->
<button matButton="filled" sharedLoadingButton (loadingClick)="onSave()">
  <mat-icon>save</mat-icon>
  Tallenna
</button>

<!-- Cancel action -->
<button matButton="outlined" (click)="onCancel()">
  <mat-icon>close</mat-icon>
  Peruuta
</button>

<!-- Navigation/add action -->
<button matButton="elevated" (click)="onAdd()">
  <mat-icon>add</mat-icon>
  Lisää uusi
</button>
```

### Icon-Only Buttons

```html
<!-- Icon-only save -->
<button matButton="filled" sharedLoadingButton (loadingClick)="onSave()">
  <mat-icon>save</mat-icon>
</button>

<!-- Icon-only close -->
<button matButton="outlined" (click)="onClose()">
  <mat-icon>close</mat-icon>
</button>

<!-- Icon-only add -->
<button matButton="elevated" (click)="onAdd()">
  <mat-icon>add</mat-icon>
</button>
```

### Dialog Button Pattern

```html
<mat-dialog-actions align="end">
  <button matButton="outlined" type="button" (click)="onCancel()">
    <mat-icon>close</mat-icon>
    Peruuta
  </button>
  <button matButton="filled"
          sharedLoadingButton
          [disabled]="!myForm().valid()"
          (loadingClick)="onSubmit()">
    <mat-icon>save</mat-icon>
    Tallenna
  </button>
</mat-dialog-actions>
```

### Destructive Action with Confirmation

```html
<button matButton="filled"
        sharedLoadingButton
        [confirm]="true"
        (loadingClick)="onDelete()">
  <mat-icon>delete</mat-icon>
  Poista
</button>
```

---

## SharedLoadingButton Directive Usage

### Required for ALL Async Operations

Every button that triggers an async operation MUST use the `sharedLoadingButton` directive.

The directive:
- Disables button during async operation
- Replaces the icon with a spinner during loading
- Restores the original icon when Promise resolves/rejects
- Prevents double-clicks
- Optional confirmation pattern (click-again-to-confirm)

### Basic Usage

**Template:**
```html
<button matButton="filled" sharedLoadingButton [loadingClick]="onSave">
  <mat-icon>save</mat-icon>
  Tallenna
</button>
```

**Component (use arrow function for 'this' binding):**
```typescript
onSave = async (): Promise<void> => {
  await this.myService.save(this.formModel());
};
```

### With Form Validation

```html
<button matButton="filled"
        sharedLoadingButton
        [disabled]="!myForm().valid()"
        [loadingClick]="onSubmit">
  <mat-icon>save</mat-icon>
  Tallenna
</button>
```

### With Confirmation Pattern

```html
<button matButton="filled"
        sharedLoadingButton
        [confirm]="true"
        [loadingClick]="onDelete">
  <mat-icon>delete</mat-icon>
  Poista
</button>
```

### PROHIBITED: Manual Loading State

Do NOT create `canSubmit` computed signals that combine form validity with loading state:

```typescript
// ❌ WRONG - Never do this
readonly canSubmit = computed(() => this.myForm().valid() && !this.isSubmitting());
```

Instead, use:
- `[disabled]="!myForm().valid()"` for form validity
- `sharedLoadingButton` directive handles loading state automatically

```html
<!-- ✅ CORRECT -->
<button matButton="filled"
        sharedLoadingButton
        [disabled]="!myForm().valid()"
        [loadingClick]="onSubmit">
  <mat-icon>save</mat-icon>
  Tallenna
</button>
```

### Component Method Pattern

Always use arrow functions for async handlers to preserve `this` binding:

```typescript
// ✅ CORRECT - Arrow function preserves 'this'
onSubmit = async (): Promise<void> => {
  if (this.myForm().valid()) {
    await this.myService.save(this.formModel());
    this.dialogRef.close(this.formModel());
  }
};

// ❌ WRONG - Regular method loses 'this' when passed as reference
async onSubmit(): Promise<void> {
  // 'this' will be undefined when called by directive
}
```

---

## Legacy Button Syntax Reference

When migrating, replace these legacy patterns:

| Legacy Syntax | New Syntax |
|---------------|------------|
| `mat-button` | `matButton` with icon inside |
| `mat-raised-button` | `matButton="elevated"` |
| `mat-flat-button` | `matButton="filled"` |
| `mat-stroked-button` | `matButton="outlined"` |
| `mat-icon-button` | `matButton` variant with `<mat-icon>` inside |
| Text-only button | Add `<mat-icon>` before text |
| `color="primary"` | Use `matButton="filled"` |
| `color="warn"` | Use `matButton="filled"` (no color needed) |
| `(click)="asyncMethod()"` | `(loadingClick)="asyncMethod()"` with `sharedLoadingButton` |

### Migration Examples

**Before:**
```html
<button mat-button (click)="onCancel()">Cancel</button>
<button mat-flat-button color="primary" (click)="onSubmit()" [disabled]="form.invalid">Save</button>
```

**After:**
```html
<button matButton="outlined" (click)="onCancel()">
  <mat-icon>close</mat-icon>
  Peruuta
</button>
<button matButton="filled"
        sharedLoadingButton
        [disabled]="!myForm().valid()"
        (loadingClick)="onSubmit()">
  <mat-icon>save</mat-icon>
  Tallenna
</button>
```

---

## Computed Signal Patterns

### Form Validity in Computed

Use `myForm().valid()` directly - do NOT create separate `isFormValid` computed:

```typescript
// ❌ WRONG - Don't create separate computed for form validity
readonly isFormValid = computed(() => this.myForm().valid());

// ✅ CORRECT - Use directly in template
// Template: [disabled]="!myForm().valid()"
```

### Derived Display State

```typescript
// Derive display text from form state
readonly submitButtonText = computed(() =>
  this.myForm().valid() ? 'Tallenna' : 'Täytä pakolliset kentät'
);

// Derive warning state
readonly showWarning = computed(() => {
  const formDirty = this.myForm().dirty();
  const hasUnsavedChanges = this.hasUnsavedChanges();
  return formDirty || hasUnsavedChanges;
});
```

### Search Criteria from Form

```typescript
// Form model
private readonly filterFormModel = signal<FilterFormModel>({
  fiscalYearId: null,
  type: null,
});

// Computed search criteria - updates automatically
readonly searchCriteria = computed<SearchCriteria>(() => {
  const model = this.filterFormModel();
  return {
    fiscalYearId: model.fiscalYearId,
    type: model.type,
  };
});
```

---

## Programmatic Form Updates

### Update Single Field

```typescript
this.formModel.update(current => ({
  ...current,
  name: 'New Value',
}));
```

### Reset Entire Form

```typescript
this.formModel.set({
  name: '',
  email: '',
  categoryId: null,
});
```

### Populate Form from Data

```typescript
private populateForm(data: DataDTO): void {
  this.formModel.set({
    name: data.name,
    email: data.email,
    categoryId: data.categoryId,
  });
}
```

### Effect for Loading Data

```typescript
constructor() {
  effect(() => {
    const data = this.externalData();
    if (data) {
      untracked(() => this.populateForm(data));
    }
  });
}
```
