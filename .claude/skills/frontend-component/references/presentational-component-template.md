# Presentational Component Template

## Non-Route Component Pattern

Presentational components receive data via inputs and emit events via outputs.
They contain no routing logic and are purely presentational.

**Note**: This template is for **feature** presentational components (in `features/<feature>/components/`).
For **shared** components (`shared/components/shared-<name>/`), see `shared-component-template.md`.

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
  inject,
  ContentChild,
  TemplateRef,
} from "@angular/core";
import { ItemDTO } from "@api/dto";
import { CoreModule } from "@core/modules";
import { MaterialModule } from "@shared/material";
import { SharedModule } from "@shared/shared.module";
import { CoreI18nService } from "@core/services";

/**
 * Item list viewer component for displaying lists
 *
 * Feature component that displays a list of items.
 * No routing logic - purely presentational.
 */
@Component({
  selector: "item-list-viewer",
  imports: [CoreModule, MaterialModule, SharedModule],
  templateUrl: "./item-list-viewer.component.html",
  styleUrls: ["./item-list-viewer.component.scss"],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ItemListViewerComponent {
  // Inject services as needed
  private i18nService = inject(CoreI18nService);

  // Component inputs using input() function
  items = input<ItemDTO[]>([]);
  showActions = input<boolean>(true);

  // Required inputs use input.required<Type>()
  // title = input.required<string>();

  // Component outputs using output() function
  itemClick = output<ItemDTO>();
  itemDelete = output<string>();

  // Content projection for custom templates
  @ContentChild("itemActions", { static: false })
  actionsTemplate?: TemplateRef<any>;

  // Computed properties derived from inputs
  hasItems = computed(() => {
    const currentItems = this.items();
    return currentItems && currentItems.length > 0;
  });

  showEmptyState = computed(() => !this.hasItems());

  itemCount = computed(() => this.items().length);

  // Event handlers - emit to parent
  onItemClick(item: ItemDTO): void {
    this.itemClick.emit(item);
  }

  onDelete(id: string): void {
    this.itemDelete.emit(id);
  }

  // TrackBy function for performance
  trackByItemId(index: number, item: ItemDTO): string {
    return item.id;
  }

  // Helper methods for template formatting
  formatDate(date: string): string {
    return this.i18nService.formatDate(date);
  }

  formatDisplayName(item: ItemDTO): string {
    return item.name || "Unnamed";
  }
}
```

## Template Pattern

**IMPORTANT**: All interactive elements, rendered values, and key content must have `data-test-id` attributes for E2E testing. See SKILL.md for full naming convention.

```html
<!-- No route-container - parent handles layout -->
<div class="item-list-viewer" data-test-id="item-list-viewer">
  @if (showEmptyState()) {
  <shared-empty-content
    icon="folder_open"
    title="No Items"
    description="No items to display."
    data-test-id="empty-state"
  >
  </shared-empty-content>
  } @else { @for (item of items(); track trackByItemId($index, item)) {
  <div class="item-row" (click)="onItemClick(item)" data-test-id="item-row-{{ item.id }}">
    <div class="item-content">
      <span class="item-name" data-test-id="item-name-{{ item.id }}">{{ formatDisplayName(item) }}</span>
      <span class="item-date" data-test-id="item-date-{{ item.id }}">{{ formatDate(item.createdAt) }}</span>
    </div>

    @if (showActions()) {
    <div class="item-actions">
      <!-- Use content projection for custom actions -->
      @if (actionsTemplate) {
      <ng-container
        *ngTemplateOutlet="actionsTemplate; context: { $implicit: item }"
      ></ng-container>
      } @else {
      <!-- Default actions -->
      <button
        mat-icon-button
        (click)="onDelete(item.id); $event.stopPropagation()"
        data-test-id="delete-btn-{{ item.id }}"
      >
        <mat-icon>delete</mat-icon>
      </button>
      }
    </div>
    }
  </div>
  } }
</div>
```

## Usage in Parent Route Component

```typescript
// In route component imports array:
imports: [CoreModule, MaterialModule, SharedModule, ItemListViewerComponent],

// In template:
<item-list-viewer
  [items]="itemsData()!"
  [showActions]="true"
  (itemClick)="onItemClick($event)"
  (itemDelete)="onItemDelete($event)"
>
  <!-- Optional custom actions template -->
  <ng-template #itemActions let-item>
    <button mat-icon-button (click)="onEdit(item)">
      <mat-icon>edit</mat-icon>
    </button>
  </ng-template>
</item-list-viewer>
```

## Export from Feature Index

```typescript
// src/ui/src/app/features/<feature>/components/index.ts
export { ItemListViewerComponent } from "./item-list-viewer/item-list-viewer.component";
```

## Key Patterns

### Input/Output Best Practices

```typescript
// Simple inputs with defaults
items = input<ItemDTO[]>([]);
enabled = input<boolean>(true);

// Required inputs (no default)
userId = input.required<string>();

// Transform inputs
count = input(0, { transform: numberAttribute });

// Outputs
itemClick = output<ItemDTO>();
delete = output<string>();
selectionChange = output<ItemDTO[]>();
```

### Computed from Inputs

```typescript
// Always use computed() for derived state
readonly isEmpty = computed(() => this.items().length === 0);
readonly selectedCount = computed(() =>
  this.items().filter(i => i.selected).length
);
readonly hasSelection = computed(() => this.selectedCount() > 0);
```

### No Effects - Use Computed Instead

```typescript
// BAD - Don't use effects
effect(() => {
  if (this.items().length > 0) {
    this.updateSomething();
  }
});

// GOOD - Use computed signals
readonly processedItems = computed(() =>
  this.items().map(item => this.transform(item))
);
```
