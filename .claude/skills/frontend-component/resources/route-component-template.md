# Route Component Template

## Pattern 1: Paginated List with Filters

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
  signal,
} from '@angular/core';
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/material';
import { SharedModule } from '@shared/shared.module';
import { SharedNotificationService } from '@shared/services';
import { FeatureService, PAGE_SIZE } from '../../services/feature.service';
import { FeatureListComponent } from '../feature-list/feature-list.component';

@Component({
  selector: 'route-feature-list',
  imports: [
    CoreModule,
    MaterialModule,
    SharedModule,
    FeatureListComponent,
  ],
  templateUrl: './route-feature-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RouteFeatureListComponent {
  private readonly service = inject(FeatureService);
  private readonly notification = inject(SharedNotificationService);

  // Filter state as simple signals
  readonly selectedParentId = signal<string>('');
  readonly selectedStatus = signal<string>('');
  readonly currentOffset = signal<number>(0);
  readonly pageSize = PAGE_SIZE;

  // Composite search derived from filters
  readonly search = computed(() => ({
    parentId: this.selectedParentId() || undefined,
    status: this.selectedStatus() || undefined,
    offset: this.currentOffset(),
  }));

  // Data from service — computed signals trigger auto-loading
  readonly items = computed(() => {
    const s = this.search();
    return this.service.items(s.parentId, s.status, s.offset)();
  });

  readonly total = computed(() => {
    const s = this.search();
    return this.service.total(s.parentId, s.status)();
  });

  // Loading = data is null
  readonly isLoading = computed(() => this.items() === null);

  // Static filter options
  readonly statusOptions = [
    { value: '', label: 'All statuses' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
  ];

  // Filter change handlers — always reset offset to 0
  protected onParentFilterChange(value: string): void {
    this.selectedParentId.set(value);
    this.currentOffset.set(0);
  }

  protected onStatusFilterChange(value: string): void {
    this.selectedStatus.set(value);
    this.currentOffset.set(0);
  }

  // Pagination
  protected onPageChange(direction: 'prev' | 'next'): void {
    const offset = this.currentOffset();
    if (direction === 'next') {
      this.currentOffset.set(offset + this.pageSize);
    } else if (offset >= this.pageSize) {
      this.currentOffset.set(offset - this.pageSize);
    }
  }

  // Action methods — arrow functions for sharedLoadingButton directive
  protected onTriggerAction = async (): Promise<void> => {
    try {
      await this.service.triggerAction(this.selectedParentId());
      this.notification.success('Action triggered successfully');
      const s = this.search();
      await this.service.search(s.parentId, s.status, s.offset);
    } catch (error: any) {
      this.notification.error('Action failed');
      throw error;
    }
  };
}
```

### Key Patterns for Paginated Lists

1. **Filter signals**: Use `signal<string>('')` for each filter, not a form model
2. **Composite search computed**: Derive search params from filter signals in one `computed()`
3. **Data computed from search**: `computed(() => { const s = this.search(); return this.service.items(...)(); })`
4. **Reset offset on filter change**: Every filter change handler calls `this.currentOffset.set(0)`
5. **PAGE_SIZE from service**: Import and expose as class property for template access
6. **Arrow functions for loading buttons**: Use `= async () =>` syntax for `sharedLoadingButton` directive

### Paginated List HTML Template

```html
<div class="page-container">
  <mat-card class="mb-md" data-test-id="feature-filters">
    <mat-card-header class="mat-card-header--with-margin">
      <mat-card-title>
        <div class="flex items-center gap-sm">
          <mat-icon>list</mat-icon>
          <span data-test-id="page-title">Items</span>
        </div>
      </mat-card-title>
    </mat-card-header>
    <mat-card-content>
      <div class="flex gap-md items-start flex-wrap">
        <mat-form-field appearance="outline" data-test-id="filter-parent-field">
          <mat-label>Parent</mat-label>
          <mat-select
            [value]="selectedParentId()"
            (selectionChange)="onParentFilterChange($event.value)"
            data-test-id="filter-parent-select"
          >
            <mat-option value="">All</mat-option>
            @for (item of parents() ?? []; track item.id) {
              <mat-option [value]="item.id">{{ item.name }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" data-test-id="filter-status-field">
          <mat-label>Status</mat-label>
          <mat-select
            [value]="selectedStatus()"
            (selectionChange)="onStatusFilterChange($event.value)"
            data-test-id="filter-status-select"
          >
            @for (opt of statusOptions; track opt.value) {
              <mat-option [value]="opt.value">{{ opt.label }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>
    </mat-card-content>
  </mat-card>

  @if (isLoading()) {
    <shared-loading-bar [loading]="true" data-test-id="loading-spinner" />
  } @else if (items()!.length === 0) {
    <shared-empty-state
      icon="folder_open"
      title="No items found"
      message="No items match the current filters."
      data-test-id="empty-state"
    />
  } @else {
    <mat-card>
      <mat-card-content>
        <app-feature-list [items]="items()!" />
      </mat-card-content>

      <mat-card-actions class="pagination-actions">
        <span data-test-id="pagination-info">
          Showing {{ currentOffset() + 1 }}&ndash;{{ currentOffset() + items()!.length }} of
          {{ total() }}
        </span>
        <div class="flex gap-sm">
          <button
            matButton
            class="btn-action"
            [disabled]="currentOffset() === 0"
            (click)="onPageChange('prev')"
            data-test-id="pagination-prev-btn"
          >
            <mat-icon>chevron_left</mat-icon>
            Previous
          </button>
          <button
            matButton
            class="btn-action"
            [disabled]="currentOffset() + pageSize >= total()"
            (click)="onPageChange('next')"
            data-test-id="pagination-next-btn"
          >
            Next
            <mat-icon>chevron_right</mat-icon>
          </button>
        </div>
      </mat-card-actions>
    </mat-card>
  }
</div>
```

---

## Pattern 2: Detail View with Related Data

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  computed,
  inject,
} from '@angular/core';
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/material';
import { SharedModule } from '@shared/shared.module';
import { CoreNavService } from '@core/services';
import { PATHS } from '@core/constants';
import { FeatureService } from '../../services/feature.service';

@Component({
  selector: 'route-feature-detail',
  imports: [CoreModule, MaterialModule, SharedModule],
  templateUrl: './route-feature-detail.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RouteFeatureDetailComponent {
  private readonly service = inject(FeatureService);
  private readonly nav = inject(CoreNavService);

  // Route param as computed
  private readonly itemId = computed(() => this.nav.routeParamMap()['id']);

  // Item from service — auto-loads via untracked when null
  readonly item = computed(() => {
    const id = this.itemId();
    if (!id) return null;
    return this.service.item(id)();
  });

  // Loading = data is null
  readonly isLoading = computed(() => this.item() === null);

  // Related data from service — auto-loads separately
  readonly logContent = computed(() => {
    const id = this.itemId();
    if (!id) return null;
    return this.service.logContent(id)();
  });

  // Derived state from loaded item
  readonly hasArtifacts = computed(() => {
    const item = this.item();
    return item !== null && item.status === 'succeeded';
  });

  // Navigation
  protected navigateBack(): void {
    this.nav.goto(PATHS.FEATURE.LIST);
  }

  // Helper methods for template
  protected getStatusClass(status: string): string {
    switch (status) {
      case 'succeeded': return 'status--succeeded';
      case 'failed': return 'status--failed';
      case 'ongoing': return 'status--ongoing';
      default: return 'status--pending';
    }
  }

  protected formatTime(timestamp: number | undefined): string {
    if (!timestamp) return '--';
    return new Date(timestamp * 1000).toLocaleString();
  }
}
```

### Key Patterns for Detail Views

1. **Route param as computed**: `computed(() => this.nav.routeParamMap()['id'])`
2. **Item from service with null guard**: `computed(() => { const id = this.itemId(); if (!id) return null; return this.service.item(id)(); })`
3. **Loading = null**: `computed(() => this.item() === null)`
4. **Related data separately computed**: Each piece of related data gets its own computed signal
5. **Derived state from item**: Additional computed signals for UI state (e.g., `hasArtifacts`)
6. **Helper methods**: Format/transform methods for the template (status classes, date formatting)
7. **No ngOnInit loading**: Services auto-load via untracked — never call load methods in ngOnInit

### Detail View HTML Template (info-grid pattern)

```html
<div class="page-container">
  @if (isLoading()) {
    <shared-loading-bar [loading]="true" data-test-id="loading-spinner" />
  } @else {
    <mat-card class="mb-md" data-test-id="item-metadata">
      <mat-card-header class="mat-card-header--with-margin">
        <mat-card-title>
          <div class="flex items-center gap-sm">
            <button matButton class="only-icon btn-back" (click)="navigateBack()" data-test-id="back-btn">
              <mat-icon>arrow_back</mat-icon>
            </button>
            <span data-test-id="page-title">Item Details</span>
          </div>
        </mat-card-title>
        <div class="page-header__actions">
          <!-- Action buttons here -->
        </div>
      </mat-card-header>
      <mat-card-content>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Name</span>
            <span class="info-value" data-test-id="item-name">{{ item()!.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Status</span>
            <span class="info-value">
              <span class="status-badge" [ngClass]="getStatusClass(item()!.status)" data-test-id="item-status">
                {{ item()!.status }}
              </span>
            </span>
          </div>
          <!-- More info-items... -->
        </div>
      </mat-card-content>
    </mat-card>
  }
</div>
```

---

## Side Note: Polling Lifecycle

For features that need real-time updates (builds, deployments), add polling in the component:

```typescript
export class RouteFeatureListComponent implements OnInit, OnDestroy {
  private pollingInterval: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.startPolling();
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }

  private startPolling(): void {
    this.pollingInterval = setInterval(async () => {
      const changed = await this.service.checkForUpdates();
      if (changed) {
        this.currentOffset.set(0);  // Reset to first page
      }
    }, 5000);
  }

  private stopPolling(): void {
    if (this.pollingInterval !== null) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }
}
```

For detail views, poll only when the item is in a transitional state:

```typescript
private startPolling(): void {
  this.pollingInterval = setInterval(async () => {
    const item = this.item();
    if (item && item.status === 'ongoing') {
      await this.loadItem();  // Refresh the item
    }
  }, 3000);
}
```

This is a **special pattern** — most components do NOT need polling.

---

## Template data-test-id Requirement

**IMPORTANT**: ALL interactive elements, rendered values, and key content must have `data-test-id` attributes. See SKILL.md for the full naming convention.

---

## Key Patterns Summary

### Service Injection

```typescript
private readonly service = inject(FeatureService);
private readonly nav = inject(CoreNavService);
private readonly notification = inject(SharedNotificationService);
```

### Loading State — CRITICAL PATTERN

```typescript
// ✅ CORRECT: Loading state derived from data being null
readonly isLoading = computed(() => this.items() === null);

// ❌ NEVER DO THIS — Manual loading with ngOnInit
// isLoading = signal(false);
// async ngOnInit() { ... }
```

### Dialog Opening via Static Method

```typescript
protected async openDialog(): Promise<void> {
  const result = await FeatureDialogComponent.open(this.dialog, { data });
  if (result) {
    await this.service.create(result);
  }
}
```

### Sorted/Filtered Data

```typescript
readonly sortedItems = computed(() => {
  const items = this.items();
  if (!items) return [];
  return [...items].sort((a, b) => a.name.localeCompare(b.name, 'fi'));
});
```
