# Component Rules Reference

## data-test-id — MANDATORY for E2E Testing

**Every component template MUST include `data-test-id` attributes on ALL important interactive and content elements.** This is critical for reliable E2E test selectors. Missing `data-test-id` attributes block test automation.

**Elements that MUST have `data-test-id`:**
- **All buttons** (submit, cancel, delete, navigation, menu triggers, icon-only buttons)
- **All form inputs** (`<input>`, `<textarea>`, `<mat-select>`, `<mat-slide-toggle>`, `<mat-checkbox>`, etc.)
- **All form fields** (`<mat-form-field>`) — put `data-test-id` on the `mat-form-field` wrapper
- **Page headings** (`<h1>`, `<h2>`, etc.) that identify the page or section
- **Table rows** (`<tr mat-row>`) — use dynamic ID with row identifier
- **Displayed data values** (status badges, amounts, names, dates) that tests may assert on
- **Links and navigation elements** that tests may click
- **Empty states and loading indicators** to verify page state
- **Dialog containers** and dialog action buttons
- **Menu items** (`<button mat-menu-item>`)

**Naming convention:** `data-test-id="<context>-<element>-<identifier>"`
- Use kebab-case
- Include the entity/context: `data-test-id="item-delete-btn"`, `data-test-id="filter-fiscal-year-select"`
- For dynamic rows/items, include the identifier: `data-test-id="item-row-{{ item.id }}"`, `data-test-id="delete-btn-{{ item.id }}"`
- For page-level elements: `data-test-id="page-title"`, `data-test-id="create-btn"`, `data-test-id="back-btn"`

**Examples:**
```html
<!-- Page header -->
<h1 data-test-id="page-title">Items</h1>
<button matButton class="btn-action" (click)="openCreateDialog()" data-test-id="create-btn">
  <mat-icon>add</mat-icon> Add new
</button>

<!-- Form inputs -->
<mat-form-field appearance="outline" data-test-id="name-field">
  <input matInput [formField]="editForm.name" data-test-id="name-input" />
</mat-form-field>
<mat-form-field appearance="outline" data-test-id="type-field">
  <mat-select [formField]="filterForm.type" data-test-id="type-select">...</mat-select>
</mat-form-field>

<!-- Table rows and cells -->
<tr mat-row *matRowDef="let row; columns: displayedColumns" data-test-id="item-row-{{ row.id }}"></tr>
<td mat-cell *matCellDef="let row" data-test-id="item-name-{{ row.id }}">{{ row.name }}</td>
<span class="status-badge" data-test-id="item-status-{{ row.id }}">{{ row.status }}</span>

<!-- Row action buttons -->
<button mat-menu-item (click)="openEditDialog(row)" data-test-id="edit-btn-{{ row.id }}">
  <mat-icon>edit</mat-icon> <span>Edit</span>
</button>
<button mat-menu-item (click)="onDelete(row)" data-test-id="delete-btn-{{ row.id }}">
  <mat-icon>delete</mat-icon> <span>Delete</span>
</button>

<!-- Empty state and loading -->
<shared-empty-state ... data-test-id="empty-state"></shared-empty-state>
<shared-loading-bar data-test-id="loading-spinner"></shared-loading-bar>
```

**Do NOT skip this.** If a template has buttons, inputs, headers, or rendered values without `data-test-id`, it is incomplete.

## Route Component Rules

1. **Services via inject()**: Use `private readonly service = inject(ServiceClass)`
2. **Route params via computed**: `itemId = computed(() => this.nav.routeParamMap()['id'])`
3. **Active data via nested computed**: `computed(() => { const id = this.itemId(); if (!id) return null; return this.service.item(id)(); })`
4. **Loading = null**: Derive loading state via `computed(() => this.data() === null)` — NEVER use `isLoading = signal(false)` with manual ngOnInit loading
5. **No ngOnInit data loading**: Services auto-load via `untracked()` when data signal is null — don't call `loadData()` manually
6. **Navigation**: Use `CoreNavService.goto()` with `PATHS` constants
7. **Error handling**: Use `SharedNotificationService` for user feedback
8. **Arrow functions**: Use arrow functions for `sharedLoadingButton` directive
9. **Empty states**: Use `<shared-empty-state>` component (NOT `shared-empty-content`)
10. **Loading states**: Use `<shared-loading-bar />` for data loading
11. **Dialog opening**: Always use static `DialogComponent.open(dialog, data)` method, never `dialog.open(...)`

### Loading State Pattern (CRITICAL)

```typescript
// WRONG PATTERN — Never do this:
export class MyComponent implements OnInit {
  isLoading = signal(false);
  data = signal<Data[] | null>(null);
  async ngOnInit() {
    this.isLoading.set(true);
    const result = await this.service.loadData();
    this.data.set(result);
    this.isLoading.set(false);
  }
}

// CORRECT PATTERN — Always do this:
export class MyComponent {
  readonly items = computed(() => {
    const s = this.search();
    return this.service.items(s.parentId, s.status, s.offset)();
  });
  readonly isLoading = computed(() => this.items() === null);
}
```

### Paginated List Pattern
- Use `signal<string>('')` for each filter, NOT form models
- Derive composite search params in one `computed()`
- Data computed from search signals
- **Reset offset on every filter change**: `this.currentOffset.set(0)`
- Import `PAGE_SIZE` from service and expose as class property

### Detail View Pattern
- Route param: `private readonly itemId = computed(() => this.nav.routeParamMap()['id'])`
- Item with null guard: `readonly item = computed(() => { const id = this.itemId(); if (!id) return null; return this.service.item(id)(); })`
- Derived state from item signal

## Presentational Component Rules

1. **Inputs**: Use `input<Type>()` function, not `@Input()` decorator
2. **Outputs**: Use `output<Type>()` function, not `@Output()` decorator
3. **Computed from inputs**: Derive state with `computed(() => this.myInput())`
4. **TrackBy**: Provide trackBy functions for `@for` loops
5. **Helper methods**: Add formatting/logic helpers for template
6. **Content projection**: Use `@ContentChild` for optional template slots

## Shared Component Rules

1. **No SharedModule import**: Only use `imports: [CoreModule, MaterialModule]` — never import SharedModule (circular dependency)
2. **Register in SharedModule**: Add to `SHARED_COMPONENTS` array in the shared module
3. **Prefix naming**: Always use `shared-` prefix (e.g., `shared-pdf-viewer`, `SharedPdfViewerComponent`)
4. **Same patterns as presentational**: Use `input()`, `output()`, `computed()`, OnPush change detection
