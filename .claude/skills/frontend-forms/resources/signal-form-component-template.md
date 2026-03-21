# Signal Form Component Templates (Patterns 4, 5, 6)

## Pattern 4: Inline Edit Form

For components with inline editing like `accounting-posting-list`.

### TypeScript Component

```typescript
import { Component, ChangeDetectionStrategy, inject, signal, computed } from '@angular/core';
import { form, FormField, required, pattern } from '@angular/forms/signals';
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/material';
import { SharedModule } from '@shared/shared.module';

interface PostingFormModel {
  amount: string;
  side: 'debit' | 'credit';
  comment: string;
}

@Component({
  selector: 'feature-posting-list',
  imports: [CoreModule, MaterialModule, SharedModule, FormField],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './feature-posting-list.component.html',
})
export class FeaturePostingListComponent {
  private readonly featureService = inject(FeatureService);

  // Edit state
  protected readonly isAddingNew = signal(false);
  protected readonly editingPostingId = signal<string | null>(null);

  // Form model
  private readonly formModel = signal<PostingFormModel>({
    amount: '',
    side: 'debit',
    comment: '',
  });

  protected readonly postingForm = form(this.formModel, (f) => {
    required(f.amount, { message: 'Amount is required' });
    pattern(f.amount, /^\d+([.,]\d{1,2})?$/, { message: 'Invalid amount format' });
  });

  // Reset form for new entry
  protected startAdd(): void {
    this.formModel.set({ amount: '', side: 'debit', comment: '' });
    this.isAddingNew.set(true);
    this.editingPostingId.set(null);
  }

  // Populate form for editing
  protected startEdit(posting: PostingDTO): void {
    this.formModel.set({
      amount: posting.amount,
      side: posting.side as 'debit' | 'credit',
      comment: posting.comment || '',
    });
    this.editingPostingId.set(posting.id);
    this.isAddingNew.set(false);
  }

  // Cancel editing
  protected cancelEdit(): void {
    this.isAddingNew.set(false);
    this.editingPostingId.set(null);
  }

  // Save inline
  protected async saveInline(): Promise<void> {
    if (!this.postingForm().valid()) return;

    const values = this.formModel();
    if (this.isAddingNew()) {
      await this.featureService.create(values);
    } else {
      const id = this.editingPostingId();
      if (id) {
        await this.featureService.update(id, values);
      }
    }

    this.cancelEdit();
  }
}
```

### HTML Template

```html
<!-- Inline edit row -->
@if (isAddingNew() || editingPostingId()) {
  <tr class="edit-row">
    <td>
      <mat-form-field appearance="outline">
        <input matInput [formField]="postingForm.amount" placeholder="Amount" />
      </mat-form-field>
    </td>
    <td>
      <mat-form-field appearance="outline">
        <mat-select [formField]="postingForm.side">
          <mat-option value="debit">Debit</mat-option>
          <mat-option value="credit">Credit</mat-option>
        </mat-select>
      </mat-form-field>
    </td>
    <td>
      <mat-form-field appearance="outline">
        <input matInput [formField]="postingForm.comment" placeholder="Comment" />
      </mat-form-field>
    </td>
    <td class="item-actions">
      <button matButton type="button" (click)="cancelEdit()">
        <mat-icon>close</mat-icon>
      </button>
      <button matButton
              sharedLoadingButton
              [disabled]="!postingForm().valid()"
              (loadingClick)="saveInline()">
        <mat-icon>save</mat-icon>
      </button>
    </td>
  </tr>
}
```

---

## Pattern 5: Route Component with Autocomplete

For route components like `route-accounting-document-detail` with autocomplete suggestions.

### TypeScript Component

```typescript
import { Component, ChangeDetectionStrategy, inject, signal, computed, effect, untracked } from '@angular/core';
import { form, FormField } from '@angular/forms/signals';
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/material';
import { SharedModule } from '@shared/shared.module';
import { CoreNavService } from '@core/services';

interface DocumentFormModel {
  type: string;
  direction: string;
  documentDate: string | null;
  description: string;
  amount: string;
  vendor: string;
  buyer: string;
}

@Component({
  selector: 'route-feature-document-detail',
  imports: [CoreModule, MaterialModule, SharedModule, FormField],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './route-feature-document-detail.component.html',
})
export class RouteFeatureDocumentDetailComponent {
  private readonly nav = inject(CoreNavService);
  private readonly documentService = inject(DocumentService);

  // Route param
  private readonly documentId = computed(() => this.nav.routeParamMap()['id'] || null);

  // Document data
  protected readonly document = computed(() => {
    const id = this.documentId();
    if (!id) return null;
    return this.documentService.getById(id)();
  });

  // Autocomplete suggestions
  protected readonly vendorSuggestions = computed(() =>
    this.documentService.getVendorSuggestions()()
  );

  // Form model
  private readonly formModel = signal<DocumentFormModel>({
    type: 'OTHER',
    direction: 'OUTGOING',
    documentDate: null,
    description: '',
    amount: '',
    vendor: '',
    buyer: '',
  });

  protected readonly documentForm = form(this.formModel);

  // Filtered autocomplete options
  protected readonly filteredVendors = computed(() => {
    const vendors = this.vendorSuggestions() || [];
    const currentValue = this.formModel().vendor.toLowerCase();
    if (!currentValue) return vendors.slice(0, 10);
    return vendors.filter(v => v.toLowerCase().includes(currentValue)).slice(0, 10);
  });

  // Populate form when document loads
  constructor() {
    effect(() => {
      const doc = this.document();
      if (doc) {
        untracked(() => this.populateForm(doc));
      }
    });
  }

  private populateForm(doc: DocumentDTO): void {
    this.formModel.set({
      type: doc.type,
      direction: doc.direction,
      documentDate: doc.documentDate || null,
      description: doc.description || '',
      amount: doc.amount || '',
      vendor: doc.vendor || '',
      buyer: doc.buyer || '',
    });
  }

  // Update single field from autocomplete selection
  protected onVendorSelected(value: string): void {
    this.formModel.update(current => ({
      ...current,
      vendor: value,
    }));
  }

  protected async onSave(): Promise<void> {
    const id = this.documentId();
    if (!id) return;

    await this.documentService.update(id, this.formModel());
  }
}
```

### HTML Template

```html
<div class="page-container">
  @if (document() === null) {
    <shared-loading-bar [loading]="true" />
  } @else {
    <h1>{{ document().title }}</h1>

    <form class="form-grid">
      <mat-form-field appearance="outline">
        <mat-label>Type</mat-label>
        <mat-select [formField]="documentForm.type">
          <mat-option value="INVOICE">Invoice</mat-option>
          <mat-option value="RECEIPT">Receipt</mat-option>
          <mat-option value="OTHER">Other</mat-option>
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Direction</mat-label>
        <mat-select [formField]="documentForm.direction">
          <mat-option value="INCOMING">Incoming</mat-option>
          <mat-option value="OUTGOING">Outgoing</mat-option>
        </mat-select>
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Vendor</mat-label>
        <input matInput [formField]="documentForm.vendor" [matAutocomplete]="vendorAuto" />
        <mat-autocomplete #vendorAuto="matAutocomplete" (optionSelected)="onVendorSelected($event.option.value)">
          @for (option of filteredVendors(); track option) {
            <mat-option [value]="option">{{ option }}</mat-option>
          }
        </mat-autocomplete>
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Amount</mat-label>
        <input matInput [formField]="documentForm.amount" />
      </mat-form-field>
    </form>

    <div class="card-actions">
      <button matButton class="btn-action" sharedLoadingButton (loadingClick)="onSave()">
        <mat-icon>save</mat-icon>
        Save
      </button>
    </div>
  }
</div>
```

---

## Pattern 6: Replacing valueChanges Subscriptions

For components that previously used `valueChanges.subscribe()` to react to form changes.

### Before (ReactiveFormsModule)

```typescript
@Component({ /* ... */ })
export class RouteDocumentListComponent implements OnInit {
  readonly filterForm = new FormGroup({
    fiscalYearId: new FormControl<string | null>(null),
    type: new FormControl<string | null>(null),
  });

  readonly searchCriteria = signal<SearchCriteria>({
    fiscalYearId: null,
    type: null,
  });

  ngOnInit(): void {
    // Subscription - needs cleanup, memory leak risk
    this.filterForm.valueChanges.subscribe(() => {
      this.searchCriteria.set({
        fiscalYearId: this.filterForm.value.fiscalYearId ?? null,
        type: this.filterForm.value.type ?? null,
      });
    });
  }
}
```

### After (Signal Forms)

```typescript
interface FilterFormModel {
  fiscalYearId: string | null;
  type: string | null;
}

@Component({ /* ... */ })
export class RouteDocumentListComponent {
  private readonly documentService = inject(DocumentService);

  // Form model is the single source of truth
  private readonly filterFormModel = signal<FilterFormModel>({
    fiscalYearId: null,
    type: null,
  });

  protected readonly filterForm = form(this.filterFormModel);

  // Search criteria is now a computed signal - automatically derived
  // No subscription needed - updates automatically when form changes
  readonly searchCriteria = computed<SearchCriteria>(() => {
    const model = this.filterFormModel();
    return {
      fiscalYearId: model.fiscalYearId,
      type: model.type,
    };
  });

  // Documents computed from search criteria - cascading reactivity
  readonly documents = computed(() => {
    const criteria = this.searchCriteria();
    if (!criteria.fiscalYearId) {
      return null;
    }
    return this.documentService.getSearchResults(criteria)();
  });

  // Derived display state
  readonly hasActiveFilters = computed(() => {
    const model = this.filterFormModel();
    return model.type !== null;
  });

  // No ngOnInit needed for form change handling!
}
```

### Template

```html
<div class="filter-section">
  <mat-form-field appearance="outline">
    <mat-label>Fiscal Year</mat-label>
    <mat-select [formField]="filterForm.fiscalYearId">
      @for (fy of fiscalYears(); track fy.id) {
        <mat-option [value]="fy.id">{{ fy.name }}</mat-option>
      }
    </mat-select>
  </mat-form-field>

  <mat-form-field appearance="outline">
    <mat-label>Type</mat-label>
    <mat-select [formField]="filterForm.type">
      <mat-option [value]="null">All</mat-option>
      <mat-option value="INVOICE">Invoice</mat-option>
      <mat-option value="RECEIPT">Receipt</mat-option>
    </mat-select>
  </mat-form-field>

  @if (hasActiveFilters()) {
    <button matButton (click)="clearFilters()">
      <mat-icon>clear</mat-icon>
      Clear filters
    </button>
  }
</div>

<div class="document-list">
  @if (documents() === null) {
    <shared-loading-bar [loading]="true" />
  } @else {
    @for (doc of documents(); track doc.id) {
      <div class="item-row">{{ doc.title }}</div>
    } @empty {
      <shared-empty-state message="No documents found" />
    }
  }
</div>
```

### Key Insight

With signal forms, the form model signal IS the reactive state. Any `computed()` that reads from `this.filterFormModel()` will automatically update when the form changes:

- No subscriptions to manage
- No cleanup needed
- No memory leak risk
- Cascading reactivity works automatically

```typescript
// This computed updates automatically when filterFormModel changes
readonly derivedValue = computed(() => {
  const model = this.filterFormModel();
  return transformValues(model);
});
```
