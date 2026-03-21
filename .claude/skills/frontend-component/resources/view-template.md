# View Template

For DOM structure, page layout, cards, info-grids, tables, buttons, and styling, see the `/frontend-design-system` skill. This file only covers loading/data and empty-list patterns.

## Loading / Data Pattern

```html
@if (isLoading()) {
  <shared-loading-bar [loading]="true" data-test-id="loading-spinner" />
} @else {
  <!-- show the data -->
}
```

## Loading / Empty / Data Pattern (List Views)

```html
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
  <!-- list content (table, cards, etc.) -->
}
```

## Empty State Component

Use `shared-empty-state` (NOT `shared-empty-content`):

```html
<shared-empty-state
  icon="folder_open"
  title="No items"
  message="Add your first item to get started."
  actionLabel="Add Item"
  (actionClick)="openCreateDialog()"
  data-test-id="empty-state"
/>
```

## Status Badge

```html
<span
  class="status-badge"
  [ngClass]="getStatusClass(row.status)"
  [attr.data-test-id]="'item-status-' + row.id"
>
  {{ row.status }}
</span>
```
