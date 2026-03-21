# Signal Form Patterns Reference

## Validation Patterns

### Available Validators

```typescript
import { required, email, minLength, maxLength, min, max, pattern } from '@angular/forms/signals';

protected readonly myForm = form(this.formModel, (f) => {
  // Required field
  required(f.name, { message: 'Name is required' });

  // Email validation
  email(f.email, { message: 'Invalid email address' });

  // Length constraints
  minLength(f.password, 8, { message: 'Password must be at least 8 characters' });
  maxLength(f.name, 100, { message: 'Name must be at most 100 characters' });

  // Numeric constraints
  min(f.amount, 0, { message: 'Amount must be positive' });
  max(f.amount, 1000000, { message: 'Amount is too large' });

  // Pattern matching
  pattern(f.code, /^[A-Z0-9]+$/, { message: 'Code may only contain uppercase letters and numbers' });
});
```

### Error Display Pattern

```html
<mat-form-field appearance="outline">
  <mat-label>Email</mat-label>
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
  required(f.email, { message: 'Email is required' });
  email(f.email, { message: 'Invalid email address' });
  maxLength(f.email, 255, { message: 'Email is too long' });
});
```

---

## Button Styling Rules (Pattern 7)

### Button Variant Mapping

| Button Purpose | Directive + CSS Class | Example |
|---------------|----------------------|---------|
| Primary action (save, confirm, search, fetch) | `matButton class="btn-action"` | Save, Submit, Search |
| Cancel/dismiss action | `matButton class="btn-cancel"` | Cancel, Close, Dismiss |
| Destructive action | `matButton class="btn-destructive"` | Delete, Remove |

See `/frontend-design-system` for the full button system with all CSS color classes.

### CRITICAL: Icon Requirements

**ALL buttons MUST have either icon-only OR icon with text. Text-only buttons are PROHIBITED.**

### Button with Icon and Text

```html
<!-- Primary action -->
<button matButton class="btn-action" sharedLoadingButton (loadingClick)="onSave()">
  <mat-icon>save</mat-icon>
  Save
</button>

<!-- Cancel action -->
<button matButton class="btn-cancel" (click)="onCancel()">
  <mat-icon>close</mat-icon>
  Cancel
</button>
```

### Icon-Only Buttons

```html
<!-- Icon-only save -->
<button matButton class="btn-action only-icon" sharedLoadingButton (loadingClick)="onSave()">
  <mat-icon>save</mat-icon>
</button>

<!-- Icon-only close -->
<button matButton class="only-icon btn-cancel" (click)="onClose()">
  <mat-icon>close</mat-icon>
</button>
```

### Dialog Button Pattern

```html
<mat-dialog-actions align="end">
  <button matButton class="btn-cancel" type="button" (click)="onCancel()">
    <mat-icon>close</mat-icon>
    Cancel
  </button>
  <button matButton class="btn-action"
          sharedLoadingButton
          [disabled]="!myForm().valid()"
          (loadingClick)="onSubmit()">
    <mat-icon>save</mat-icon>
    Save
  </button>
</mat-dialog-actions>
```

### Destructive Action with Confirmation

```html
<button matButton class="btn-destructive"
        sharedLoadingButton
        [confirm]="true"
        (loadingClick)="onDelete()">
  <mat-icon>delete</mat-icon>
  Delete
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
<button matButton sharedLoadingButton [loadingClick]="onSave">
  <mat-icon>save</mat-icon>
  Save
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
<button matButton
        sharedLoadingButton
        [disabled]="!myForm().valid()"
        [loadingClick]="onSubmit">
  <mat-icon>save</mat-icon>
  Save
</button>
```

### With Confirmation Pattern

```html
<button matButton
        sharedLoadingButton
        [confirm]="true"
        [loadingClick]="onDelete">
  <mat-icon>delete</mat-icon>
  Delete
</button>
```

### PROHIBITED: Manual Loading State

Do NOT create `canSubmit` computed signals that combine form validity with loading state:

```typescript
// WRONG - Never do this
readonly canSubmit = computed(() => this.myForm().valid() && !this.isSubmitting());
```

Instead, use:
- `[disabled]="!myForm().valid()"` for form validity
- `sharedLoadingButton` directive handles loading state automatically

```html
<!-- CORRECT -->
<button matButton
        sharedLoadingButton
        [disabled]="!myForm().valid()"
        [loadingClick]="onSubmit">
  <mat-icon>save</mat-icon>
  Save
</button>
```

### Component Method Pattern

Always use arrow functions for async handlers to preserve `this` binding:

```typescript
// CORRECT - Arrow function preserves 'this'
onSubmit = async (): Promise<void> => {
  if (this.myForm().valid()) {
    await this.myService.save(this.formModel());
    this.dialogRef.close(this.formModel());
  }
};

// WRONG - Regular method loses 'this' when passed as reference
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
| `mat-raised-button` | `matButton` with CSS class |
| `mat-flat-button` | `matButton` with CSS class |
| `mat-stroked-button` | `matButton` with CSS class |
| `mat-icon-button` | `matButton class="only-icon"` with `<mat-icon>` inside |
| Text-only button | Add `<mat-icon>` before text |
| `color="primary"` | `matButton class="btn-action"` |
| `color="warn"` | `matButton class="btn-destructive"` |
| `(click)="asyncMethod()"` | `(loadingClick)="asyncMethod()"` with `sharedLoadingButton` |

### Migration Examples

**Before:**
```html
<button mat-button (click)="onCancel()">Cancel</button>
<button mat-flat-button color="primary" (click)="onSubmit()" [disabled]="form.invalid">Save</button>
```

**After:**
```html
<button matButton class="btn-cancel" (click)="onCancel()">
  <mat-icon>close</mat-icon>
  Cancel
</button>
<button matButton class="btn-action"
        sharedLoadingButton
        [disabled]="!myForm().valid()"
        [loadingClick]="onSubmit">
  <mat-icon>save</mat-icon>
  Save
</button>
```

---

## Computed Signal Patterns

### Form Validity in Computed

Use `myForm().valid()` directly - do NOT create separate `isFormValid` computed:

```typescript
// WRONG - Don't create separate computed for form validity
readonly isFormValid = computed(() => this.myForm().valid());

// CORRECT - Use directly in template
// Template: [disabled]="!myForm().valid()"
```

### Derived Display State

```typescript
// Derive display text from form state
readonly submitButtonText = computed(() =>
  this.myForm().valid() ? 'Save' : 'Fill required fields'
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
