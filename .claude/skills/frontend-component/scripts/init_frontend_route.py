#!/usr/bin/env python3
"""
Initialize a dummy Angular route component with signal-based patterns.

Usage:
    python .claude/skills/frontend-component/scripts/init_frontend_route.py <feature> <route-name>

Example:
    python .claude/skills/frontend-component/scripts/init_frontend_route.py accounting posting-list

This creates:
    src/ui/src/app/features/accounting/components/route-accounting-posting-list/
        route-accounting-posting-list.component.ts
        route-accounting-posting-list.component.html
"""

import os
import sys
from pathlib import Path


def to_pascal_case(kebab_name: str) -> str:
    """Convert kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in kebab_name.split("-"))


def create_route_component(feature: str, route_name: str):
    """Create a route component with minimal skeleton."""

    feature_pascal = to_pascal_case(feature)
    route_pascal = to_pascal_case(route_name)

    # Full component name: RouteAccountingPostingListComponent
    component_name = f"Route{feature_pascal}{route_pascal}Component"
    selector = f"route-{feature}-{route_name}"
    folder_name = f"route-{feature}-{route_name}"

    # Paths
    base_path = Path("src/ui/src/app/features") / feature / "components" / folder_name
    ts_file = base_path / f"{folder_name}.component.ts"
    html_file = base_path / f"{folder_name}.component.html"

    # Create directory
    base_path.mkdir(parents=True, exist_ok=True)

    # TypeScript content
    ts_content = f'''import {{ Component, ChangeDetectionStrategy, inject, signal, computed, effect, untracked }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';
import {{ MatDialog }} from '@angular/material/dialog';
import {{ form, FormField }} from '@angular/forms/signals';
import {{ CoreModule }} from '@core/core.module';
import {{ MaterialModule }} from '@shared/material';
import {{ SharedModule }} from '@shared/shared.module';
import {{ CoreNavService }} from '@core/services';
import {{ PATHS }} from '@core/constants';
// TODO: Import DTOs from @api/index
// TODO: Import services from ../../services

@Component({{
  selector: '{selector}',
  imports: [CommonModule, FormField, CoreModule, MaterialModule, SharedModule],
  templateUrl: './{folder_name}.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
}})
export class {component_name} {{
  // TODO: Inject services
  private readonly dialog = inject(MatDialog);
  private readonly nav = inject(CoreNavService);

  // TODO: Define data signals from services
  // readonly items = this.itemService.getAll();

  // TODO: Define filter form if needed
  // private readonly filterFormModel = signal<FilterFormModel>({{
  //   fiscalYearId: null,
  // }});
  // protected readonly filterForm = form(this.filterFormModel);

  // TODO: Define computed signals for search/filter
  // readonly sortedItems = computed(() => {{
  //   const items = this.items();
  //   if (!items) return [];
  //   return [...items].sort((a, b) => a.name.localeCompare(b.name, 'fi'));
  // }});

  readonly displayedColumns: string[] = []; // TODO: Define columns

  constructor() {{
    // TODO: Add effect for auto-initialization if needed
    // effect(() => {{
    //   const data = this.someSignal();
    //   if (data && !this.filterFormModel().someField) {{
    //     untracked(() => {{
    //       this.filterFormModel.update(current => ({{ ...current, someField: data[0].id }}));
    //     }});
    //   }}
    // }});
  }}

  // TODO: Add dialog opening methods
  // protected async openCreateDialog(): Promise<void> {{
  //   const result = await SomeDialogComponent.open(this.dialog, {{ isEdit: false }});
  //   if (result) {{
  //     await this.someService.create(result);
  //   }}
  // }}

  protected goBack(): void {{
    this.nav.goto(PATHS.COMMON.HOME); // TODO: Update path
  }}
}}
'''

    # HTML content
    html_content = f'''<div class="page-container">
  <mat-card class="mb-md" data-test-id="page-header">
    <mat-card-header class="mat-card-header--with-margin">
      <mat-card-title>
        <div class="flex items-center gap-sm">
          <button matButton class="only-icon btn-back" (click)="goBack()" data-test-id="back-btn">
            <mat-icon>arrow_back</mat-icon>
          </button>
          <span data-test-id="page-title">TODO: Title</span>
        </div>
      </mat-card-title>
      <div class="page-header__actions">
        <!-- TODO: Add action buttons -->
        <!-- <button matButton class="btn-action" (click)="openCreateDialog()" data-test-id="create-btn">
          <mat-icon>add</mat-icon>
          Add new
        </button> -->
      </div>
    </mat-card-header>
  </mat-card>

  <!-- TODO: Add filter card if needed -->
  <!-- <mat-card class="mb-md" data-test-id="filters">
    <mat-card-content>
      <div class="flex gap-md items-start flex-wrap">
        <mat-form-field appearance="outline" data-test-id="filter-field">
          <mat-label>Filter</mat-label>
          <mat-select [formField]="filterForm.someField">
            @for (opt of options(); track opt.id) {{
              <mat-option [value]="opt.id">{{{{ opt.name }}}}</mat-option>
            }}
          </mat-select>
        </mat-form-field>
      </div>
    </mat-card-content>
  </mat-card> -->

  <!-- TODO: Add loading/empty/content states -->
  <!-- @if (items() === null) {{
    <shared-loading-bar [loading]="true" data-test-id="loading-spinner" />
  }} @else if (sortedItems().length === 0) {{
    <shared-empty-state
      icon="folder_open"
      title="No data"
      message="Add the first item to get started."
      data-test-id="empty-state"
    />
  }} @else {{
    <mat-card>
      <mat-card-content>
        <div class="table-scroll">
          <table mat-table [dataSource]="sortedItems()" class="data-table" data-test-id="items-table">
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Name</th>
              <td mat-cell *matCellDef="let row" [attr.data-test-id]="'item-name-' + row.id">{{{{ row.name }}}}</td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef></th>
              <td mat-cell *matCellDef="let row" class="actions-cell">
                <button matButton class="only-icon" [matMenuTriggerFor]="menu" [attr.data-test-id]="'menu-btn-' + row.id">
                  <mat-icon>more_vert</mat-icon>
                </button>
                <mat-menu #menu="matMenu">
                  <button mat-menu-item (click)="openEditDialog(row)" [attr.data-test-id]="'edit-btn-' + row.id">
                    <mat-icon>edit</mat-icon>
                    <span>Edit</span>
                  </button>
                </mat-menu>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns" [attr.data-test-id]="'item-row-' + row.id"></tr>
          </table>
        </div>
      </mat-card-content>
    </mat-card>
  }} -->
</div>
'''

    # Write files
    ts_file.write_text(ts_content)
    html_file.write_text(html_content)

    print(f"Created route component:")
    print(f"  {ts_file}")
    print(f"  {html_file}")
    print()
    print(f"Component: {component_name}")
    print(f"Selector: {selector}")
    print()
    print("TODO:")
    print("  1. Import DTOs from @api/index")
    print("  2. Import and inject services")
    print("  3. Define data signals from services")
    print("  4. Define filter form model and validators if needed")
    print("  5. Add computed signals for sorting/filtering")
    print("  6. Define displayedColumns array")
    print("  7. Add dialog opening methods")
    print("  8. Update HTML template with actual content")
    print("  9. Add route to app.routes.ts and PATHS constant")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python .claude/skills/frontend-component/scripts/init_frontend_route.py <feature> <route-name>")
        print("Example: python .claude/skills/frontend-component/scripts/init_frontend_route.py accounting posting-list")
        sys.exit(1)

    feature = sys.argv[1]
    route_name = sys.argv[2]

    create_route_component(feature, route_name)
