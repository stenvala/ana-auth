# View Template

## List View HTML Pattern with Page Header and Table

The primary pattern for list views uses `page-container`, `page-header`, and `data-table` classes from global styles.

```html
<div class="page-container">
  <header class="page-header">
    <div class="page-header__icon">
      <button matButton class="only-icon" (click)="goBack()" matTooltip="Takaisin" data-test-id="back-btn">
        <mat-icon>arrow_back</mat-icon>
      </button>
    </div>
    <h1 data-test-id="page-title">Items</h1>
    <div class="page-header__actions">
      <mat-slide-toggle [checked]="showInactive()" (change)="onToggleInactive()" data-test-id="show-inactive-toggle">
        Näytä myös passiiviset
      </mat-slide-toggle>
      <button matButton="filled" (click)="openCreateDialog()" data-test-id="create-btn">
        <mat-icon>add</mat-icon>
        Lisää uusi
      </button>
    </div>
  </header>

  @if (isLoading()) {
    <div class="loading-state" data-test-id="loading-state">
      <mat-spinner diameter="40"></mat-spinner>
    </div>
  } @else if (sortedItems().length === 0) {
    <shared-empty-state
      icon="folder_open"
      title="Ei tietoja"
      message="Lisää ensimmäinen kohde aloittaaksesi."
      actionLabel="Lisää uusi"
      (actionClick)="openCreateDialog()"
      data-test-id="empty-state"
    >
    </shared-empty-state>
  } @else {
    <table mat-table [dataSource]="sortedItems()" class="data-table" data-test-id="items-table">
      <!-- Name Column -->
      <ng-container matColumnDef="name">
        <th mat-header-cell *matHeaderCellDef>Nimi</th>
        <td mat-cell *matCellDef="let row" data-test-id="item-name-{{ row.id }}">{{ row.name }}</td>
      </ng-container>

      <!-- Status Column -->
      <ng-container matColumnDef="status">
        <th mat-header-cell *matHeaderCellDef>Tila</th>
        <td mat-cell *matCellDef="let row">
          <span class="status-badge" [ngClass]="row.isActive ? 'status--active' : 'status--inactive'" data-test-id="item-status-{{ row.id }}">
            {{ row.isActive ? 'Aktiivinen' : 'Passiivinen' }}
          </span>
        </td>
      </ng-container>

      <!-- Actions Column -->
      <ng-container matColumnDef="actions">
        <th mat-header-cell *matHeaderCellDef></th>
        <td mat-cell *matCellDef="let row" class="actions-cell">
          <button matButton class="only-icon" [matMenuTriggerFor]="menu" aria-label="Toiminnot" data-test-id="actions-menu-btn-{{ row.id }}">
            <mat-icon>more_vert</mat-icon>
          </button>
          <mat-menu #menu="matMenu">
            <button mat-menu-item (click)="openEditDialog(row)" data-test-id="edit-btn-{{ row.id }}">
              <mat-icon>edit</mat-icon>
              <span>Muokkaa</span>
            </button>
            <button mat-menu-item (click)="onDelete(row)" class="delete-action" data-test-id="delete-btn-{{ row.id }}">
              <mat-icon>delete</mat-icon>
              <span>Poista</span>
            </button>
          </mat-menu>
        </td>
      </ng-container>

      <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
      <tr mat-row *matRowDef="let row; columns: displayedColumns" data-test-id="item-row-{{ row.id }}"></tr>
    </table>
  }
</div>
```

## List View with Filter Card

For views with filters, use `filter-card` and `filter-form` classes.

```html
<div class="page-container">
  <header class="page-header">
    <h1 data-test-id="page-title">Kirjaukset</h1>
  </header>

  <mat-card class="filter-card" data-test-id="filter-card">
    <mat-card-content>
      <div class="filter-form">
        <mat-form-field appearance="outline" data-test-id="filter-fiscal-year-field">
          <mat-label>Tilikausi</mat-label>
          <mat-select [formField]="filterForm.fiscalYearId" data-test-id="filter-fiscal-year-select">
            @for (fy of fiscalYears(); track fy.id) {
              <mat-option [value]="fy.id" data-test-id="fiscal-year-option-{{ fy.id }}">{{ fy.name }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline" data-test-id="filter-type-field">
          <mat-label>Tyyppi</mat-label>
          <mat-select [formField]="filterForm.type" data-test-id="filter-type-select">
            @for (opt of typeOptions; track opt.value) {
              <mat-option [value]="opt.value">{{ opt.label }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>
    </mat-card-content>
  </mat-card>

  @if (items() === null) {
    <div class="loading-state" data-test-id="loading-state">
      <mat-spinner diameter="40"></mat-spinner>
    </div>
  } @else if (items()!.length === 0) {
    <shared-empty-state
      icon="receipt_long"
      title="Ei kirjauksia"
      message="Kirjauksia ei löydy valituilla suodattimilla."
      data-test-id="empty-state"
    >
    </shared-empty-state>
  } @else {
    <table mat-table [dataSource]="items()!" class="data-table" data-test-id="items-table">
      <!-- columns... -->
      <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
      <tr mat-row *matRowDef="let row; columns: displayedColumns" class="clickable-row" (click)="viewItem(row)" data-test-id="item-row-{{ row.id }}"></tr>
    </table>
  }
</div>
```

## Key Template Patterns

### Loading State (Centered)

Use the `loading-state` class from `_pages.scss`:

```html
@if (isLoading()) {
  <div class="loading-state" data-test-id="loading-state">
    <mat-spinner diameter="40"></mat-spinner>
  </div>
}
```

Or use `shared-loading-spinner` directly without wrapper:

```html
@if (document() === null) {
  <shared-loading-spinner data-test-id="loading-spinner"></shared-loading-spinner>
}
```

### Empty State

Use `shared-empty-state` component (NOT `shared-empty-content`):

```html
<shared-empty-state
  icon="folder_open"
  title="Ei tietoja"
  message="Lisää ensimmäinen kohde aloittaaksesi."
  actionLabel="Lisää uusi"
  (actionClick)="openCreateDialog()"
  data-test-id="empty-state"
>
</shared-empty-state>
```

### Page Header with Back Button and Actions

```html
<header class="page-header">
  <div class="page-header__icon">
    <button matButton class="only-icon" (click)="goBack()" matTooltip="Takaisin" data-test-id="back-btn">
      <mat-icon>arrow_back</mat-icon>
    </button>
  </div>
  <h1 data-test-id="page-title">Page Title</h1>
  <div class="page-header__actions">
    <button matButton="filled" (click)="onCreate()" data-test-id="create-btn">
      <mat-icon>add</mat-icon>
      Lisää uusi
    </button>
  </div>
</header>
```

### Table with Clickable Rows

```html
<table mat-table [dataSource]="items()" class="data-table" data-test-id="items-table">
  <!-- columns... -->
  <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
  <tr mat-row *matRowDef="let row; columns: displayedColumns" class="clickable-row" (click)="onRowClick(row)" data-test-id="item-row-{{ row.id }}"></tr>
</table>
```

### Row Actions Menu

```html
<ng-container matColumnDef="actions">
  <th mat-header-cell *matHeaderCellDef></th>
  <td mat-cell *matCellDef="let row" class="actions-cell">
    <button matButton class="only-icon" [matMenuTriggerFor]="menu" aria-label="Toiminnot" data-test-id="actions-menu-btn-{{ row.id }}">
      <mat-icon>more_vert</mat-icon>
    </button>
    <mat-menu #menu="matMenu">
      <button mat-menu-item (click)="openEditDialog(row)" data-test-id="edit-btn-{{ row.id }}">
        <mat-icon>edit</mat-icon>
        <span>Muokkaa</span>
      </button>
      <button mat-menu-item (click)="onDelete(row)" class="delete-action" data-test-id="delete-btn-{{ row.id }}">
        <mat-icon>delete</mat-icon>
        <span>Poista</span>
      </button>
    </mat-menu>
  </td>
</ng-container>
```

### Status Badge

```html
<span class="status-badge" [ngClass]="row.isActive ? 'status--active' : 'status--inactive'" data-test-id="item-status-{{ row.id }}">
  {{ row.isActive ? 'Aktiivinen' : 'Passiivinen' }}
</span>
```

## Available Global CSS Classes

From `src/ui/src/styles/_pages.scss`:
- `page-container`, `page-container--narrow`, `page-container--wide`, `page-container--fullscreen`
- `page-header`, `page-header__icon`, `page-header__actions`, `page-header__info`
- `filter-card`, `filter-form`
- `loading-state`
- `info-grid`, `info-grid--compact`, `info-item`, `info-label`, `info-value`
- `edit-form`, `edit-form--grid`, `edit-form__actions`

From `src/ui/src/styles/_components.scss`:
- `data-table`, `clickable-row`, `actions-cell`
- `status-badge`, `status--active`, `status--inactive`
- `badge`, `badge--income`, `badge--expense`
- `delete-action`
