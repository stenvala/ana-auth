# Route Component Template

## Controller Component Pattern

Route components handle routing, loading states, and navigation.
They inject services and use computed signals for reactive data flow.

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  signal,
  computed,
  inject,
  effect,
  untracked,
} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { form, FormField } from '@angular/forms/signals';
import { CommonModule } from '@angular/common';
import { CoreModule } from '@core/core.module';
import { MaterialModule, SharedModule } from '@shared/index';
import { CoreNavService } from '@core/services';
import { PATHS } from '@core/constants';
import { ItemDTO, ItemTypeEnum } from '@api/index';
import { FeatureItemService, FeatureFiscalYearService } from '../../services';
import { FeatureDialogItemComponent } from '../feature-dialog-item/feature-dialog-item.component';

interface FilterFormModel {
  fiscalYearId: string | null;
  type: ItemTypeEnum | null;
}

@Component({
  selector: 'route-feature-item-list',
  imports: [CommonModule, FormField, CoreModule, MaterialModule, SharedModule],
  templateUrl: './route-feature-item-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RouteFeatureItemListComponent {
  // Service injection via inject()
  private readonly itemService = inject(FeatureItemService);
  private readonly fiscalYearService = inject(FeatureFiscalYearService);
  private readonly dialog = inject(MatDialog);
  private readonly nav = inject(CoreNavService);

  // Data from services - computed signals trigger auto-loading
  readonly fiscalYears = this.fiscalYearService.getAll();

  // Filter form model - single source of truth
  private readonly filterFormModel = signal<FilterFormModel>({
    fiscalYearId: null,
    type: null,
  });

  protected readonly filterForm = form(this.filterFormModel);

  // Search criteria derived from form model - no subscription needed
  readonly searchCriteria = computed(() => {
    const model = this.filterFormModel();
    return {
      fiscalYearId: model.fiscalYearId,
      type: model.type,
    };
  });

  // Items computed from search criteria - cascading reactivity
  readonly items = computed(() => {
    const criteria = this.searchCriteria();
    if (!criteria.fiscalYearId) return null;
    return this.itemService.getSearchResults(criteria)();
  });

  // Sorted items for display
  readonly sortedItems = computed(() => {
    const items = this.items();
    if (!items) return [];
    return [...items].sort((a, b) => a.name.localeCompare(b.name, 'fi'));
  });

  // UI state
  readonly showInactive = signal(false);

  readonly displayedColumns = ['name', 'status', 'actions'];

  readonly typeOptions = [
    { value: null, label: 'Kaikki' },
    { value: ItemTypeEnum.TYPE_A, label: 'Tyyppi A' },
    { value: ItemTypeEnum.TYPE_B, label: 'Tyyppi B' },
  ];

  constructor() {
    // Auto-select first open fiscal year when data loads
    effect(() => {
      const fiscalYears = this.fiscalYears();
      const currentFiscalYearId = this.filterFormModel().fiscalYearId;
      if (fiscalYears && fiscalYears.length > 0 && !currentFiscalYearId) {
        const openYear = fiscalYears.find(fy => fy.status === 'OPEN') || fiscalYears[0];
        untracked(() => {
          this.filterFormModel.update(current => ({
            ...current,
            fiscalYearId: openYear.id,
          }));
        });
      }
    });
  }

  // Dialog opening via static open method
  protected async openCreateDialog(): Promise<void> {
    const result = await FeatureDialogItemComponent.open(this.dialog, {
      isEdit: false,
    });
    if (result) {
      await this.itemService.create(result);
    }
  }

  protected async openEditDialog(item: ItemDTO): Promise<void> {
    const result = await FeatureDialogItemComponent.open(this.dialog, {
      isEdit: true,
      name: item.name,
    });
    if (result) {
      await this.itemService.update(item.id, result);
    }
  }

  // Toggle handlers
  protected onToggleInactive(): void {
    this.showInactive.update(v => !v);
  }

  // Navigation
  protected goBack(): void {
    this.nav.goto(PATHS.COMMON.HOME);
  }

  protected viewItem(item: ItemDTO): void {
    this.nav.goto(PATHS.FEATURE.ITEM_DETAIL, { itemId: item.id });
  }
}
```

## Template data-test-id Requirement

**IMPORTANT**: When creating the HTML template for a route component, ALL interactive elements, rendered values, and key content must have `data-test-id` attributes for E2E testing. This includes all buttons, inputs, selects, toggles, page titles, table rows, cell values, status badges, loading states, and empty states. See SKILL.md for the full naming convention and required element list.

## Key Patterns

### Service Injection

```typescript
// Use inject() function with readonly modifier
private readonly itemService = inject(FeatureItemService);
private readonly fiscalYearService = inject(FeatureFiscalYearService);
private readonly dialog = inject(MatDialog);
private readonly nav = inject(CoreNavService);
```

### Data from Services via Computed Signals

```typescript
// Services return signals that auto-load data
readonly fiscalYears = this.fiscalYearService.getAll();

// For search-based data, derive from form model
readonly items = computed(() => {
  const criteria = this.searchCriteria();
  if (!criteria.fiscalYearId) return null;
  return this.itemService.getSearchResults(criteria)();
});
```

### Filter Form with Signal Forms

```typescript
interface FilterFormModel {
  fiscalYearId: string | null;
  type: string | null;
}

// Form model as signal - single source of truth
private readonly filterFormModel = signal<FilterFormModel>({
  fiscalYearId: null,
  type: null,
});

protected readonly filterForm = form(this.filterFormModel);

// Search criteria derived automatically
readonly searchCriteria = computed(() => {
  const model = this.filterFormModel();
  return {
    fiscalYearId: model.fiscalYearId,
    type: model.type,
  };
});
```

### Auto-Initialize Form via Effect

```typescript
constructor() {
  effect(() => {
    const fiscalYears = this.fiscalYears();
    const currentFiscalYearId = this.filterFormModel().fiscalYearId;
    if (fiscalYears && fiscalYears.length > 0 && !currentFiscalYearId) {
      const openYear = fiscalYears.find(fy => fy.status === 'OPEN') || fiscalYears[0];
      untracked(() => {
        this.filterFormModel.update(current => ({
          ...current,
          fiscalYearId: openYear.id,
        }));
      });
    }
  });
}
```

### Dialog Opening via Static Method

```typescript
// Always use static open method - never firstValueFrom(dialog.open(...).afterClosed())
protected async openCreateDialog(): Promise<void> {
  const result = await FeatureDialogItemComponent.open(this.dialog, {
    isEdit: false,
  });
  if (result) {
    await this.itemService.create(result);
  }
}
```

### Loading State - CRITICAL PATTERN

```typescript
// ✅ CORRECT: Loading state derived from data being null
readonly isLoading = computed(() => this.items() === null);

// ❌ NEVER DO THIS - Manual loading with ngOnInit
// isLoading = signal(false);
// async ngOnInit() {
//   this.isLoading.set(true);
//   await this.service.loadData();
//   this.isLoading.set(false);
// }
```

Services handle auto-loading internally:
```typescript
// In service - auto-load when signal accessed
getAll(): Signal<Data[] | null> {
  const signal = this.state.get();
  if (signal() === null) {
    untracked(() => this.loadAll());
  }
  return signal;
}
```

### Sorted/Filtered Data

```typescript
readonly sortedItems = computed(() => {
  const items = this.items();
  if (!items) return [];
  const filtered = this.showInactive() ? items : items.filter(i => i.isActive);
  return [...filtered].sort((a, b) => a.name.localeCompare(b.name, 'fi'));
});
```

## Detail Component Pattern

For detail/edit views that load a single item by route param:

```typescript
export class RouteFeatureItemDetailComponent {
  private readonly itemService = inject(FeatureItemService);
  private readonly nav = inject(CoreNavService);

  // Route param as computed - NEVER use signal + ngOnInit
  readonly itemId = computed(() => this.nav.routeParamMap()['itemId']);

  // Check for "new" mode
  readonly isNew = computed(() => this.nav.routeParamMap()['itemId'] === 'new');

  // Item from service - auto-loads when accessed
  readonly item = computed(() => {
    const id = this.itemId();
    if (!id || this.isNew()) return null;
    return this.itemService.getById(id)();
  });

  // Loading derived from item being null (when not in new mode)
  readonly isLoading = computed(() => {
    if (this.isNew()) return false;
    return this.item() === null;
  });

  // Form model as signal
  private readonly formModel = signal<FormModel>({ name: '', ... });
  protected readonly editForm = form(this.formModel);

  constructor() {
    // Populate form when item loads OR set defaults for new
    effect(() => {
      const isNew = this.isNew();
      const item = this.item();

      untracked(() => {
        if (isNew) {
          this.setDefaults();
        } else if (item) {
          this.populateForm(item);
        }
      });
    });
  }

  private setDefaults(): void {
    this.formModel.set({ name: 'Default', ... });
  }

  private populateForm(item: ItemDTO): void {
    this.formModel.set({
      name: item.name,
      ...
    });
  }
}
```
