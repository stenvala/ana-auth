---
name: frontend-forms
description: Create Angular 21 signal-based form components with validation
---

# Frontend Forms Creation

Create Angular 21 signal-based form components using the modern `@angular/forms/signals` API.

## When to Use

- Creating form dialogs (create/edit operations)
- Building forms in route components (filters, search, inline edit)
- Any component that needs form validation and field binding

## Prerequisites

1. Angular 21.x installed
2. Feature module/structure exists

## Core Imports

```typescript
import { form, FormField, required, email, minLength, maxLength, pattern, min, max } from '@angular/forms/signals';
```

## Instructions

### 1. Define Form Model Interface

```typescript
interface MyFormModel {
  name: string;
  email: string;
  categoryId: string | null;
}
```

### 2. Create Form Model Signal

```typescript
private readonly formModel = signal<MyFormModel>({ name: '', email: '', categoryId: null });
```

### 3. Create Field Tree with Validation

```typescript
protected readonly myForm = form(this.formModel, (f) => {
  required(f.name, { message: 'Name is required' });
  required(f.email, { message: 'Email is required' });
  email(f.email, { message: 'Invalid email address' });
});
```

### 4. Bind Fields in Template

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

### 5. Handle Submission

```typescript
protected onSubmit(): void {
  if (this.myForm().valid()) {
    this.dialogRef.close(this.formModel());
  }
}
```

### 6. Verify Build

```bash
source ~/.nvm/nvm.sh && nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development 2>&1 | head -20
```

## Key Rules

### Form Model
1. **Interface first**: Always define a TypeScript interface for the form model
2. **Signal wrapper**: Wrap the model in `signal<T>()`
3. **Nullable fields**: Use `string | null` for optional fields

### Validation
4. **Schema validators**: Use `required()`, `email()`, `minLength()`, etc. from `@angular/forms/signals`
5. **English messages**: All validation messages MUST be in English

### Template Binding
6. **[formField] directive**: Use `[formField]="myForm.fieldName"` for binding
7. **Error display**: Use `@if` with `invalid()` AND `touched()` conditions

### Form State
8. **Form validity**: Use `myForm().valid()` directly — do NOT create separate `isFormValid` computed
9. **Computed signals**: Use `computed()` to derive state from form model — no subscriptions
10. **No canSubmit computed**: Use `[disabled]="!myForm().valid()"` and let directive handle loading

### Button Rules (CRITICAL)
11. **Button styling**: Use bare `matButton` with CSS classes (`btn-action`, `btn-cancel`). See `/frontend-design-system`
12. **Loading button**: ALL async buttons MUST use `sharedLoadingButton` directive with `(loadingClick)`
13. **Icons required**: ALL buttons MUST have icon-only OR icon with text

### Standard Dialog Actions
```html
<mat-dialog-actions align="end">
  <button matButton class="btn-cancel" type="button" (click)="onCancel()">
    <mat-icon>close</mat-icon> Cancel
  </button>
  <button matButton class="btn-action" type="button" [disabled]="!myForm().valid()" (click)="onSubmit()">
    <mat-icon>save</mat-icon> Save
  </button>
</mat-dialog-actions>
```

## Resources

| Resource | Contents |
|----------|----------|
| `resources/signal-form-dialog-template.md` | Dialog form pattern (Pattern 1) |
| `resources/signal-form-component-template.md` | Route component form patterns (Pattern 4, 5, 6) |
| `resources/signal-form-patterns.md` | Validation, button styling, and valueChanges replacement patterns |
| `resources/form-scenarios.md` | Common form scenarios (text, select, checkbox, date, autocomplete) and available validators |

