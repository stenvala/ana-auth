#!/usr/bin/env python3
"""
Initialize a dummy Angular presentational component.

Usage:
    python .claude/skills/frontend-component/scripts/init_frontend_component.py <feature> <component-name>

Example:
    python .claude/skills/frontend-component/scripts/init_frontend_component.py accounting posting-list-viewer

This creates:
    src/ui/src/app/features/accounting/components/accounting-posting-list-viewer/
        accounting-posting-list-viewer.component.ts
        accounting-posting-list-viewer.component.html
"""

import os
import sys
from pathlib import Path


def to_pascal_case(kebab_name: str) -> str:
    """Convert kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in kebab_name.split("-"))


def create_presentational_component(feature: str, component_name: str):
    """Create a presentational component with minimal skeleton."""

    feature_pascal = to_pascal_case(feature)
    component_pascal = to_pascal_case(component_name)

    # Full component name: AccountingPostingListViewerComponent
    full_component_name = f"{feature_pascal}{component_pascal}Component"
    selector = f"{feature}-{component_name}"
    folder_name = f"{feature}-{component_name}"

    # Paths
    base_path = Path("src/ui/src/app/features") / feature / "components" / folder_name
    ts_file = base_path / f"{folder_name}.component.ts"
    html_file = base_path / f"{folder_name}.component.html"

    # Create directory
    base_path.mkdir(parents=True, exist_ok=True)

    # TypeScript content
    ts_content = f'''import {{ Component, ChangeDetectionStrategy, input, output, computed }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';
import {{ CoreModule }} from '@core/core.module';
import {{ MaterialModule, SharedModule }} from '@shared/index';
// TODO: Import DTOs from @api/index

@Component({{
  selector: '{selector}',
  imports: [CommonModule, CoreModule, MaterialModule, SharedModule],
  templateUrl: './{folder_name}.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
}})
export class {full_component_name} {{
  // TODO: Define inputs using input() function
  // readonly items = input.required<ItemDTO[]>();
  // readonly showActions = input<boolean>(true);

  // TODO: Define outputs using output() function
  // readonly itemClick = output<ItemDTO>();
  // readonly deleteClick = output<string>();

  // TODO: Define computed signals from inputs
  // readonly sortedItems = computed(() => {{
  //   return [...this.items()].sort((a, b) => a.name.localeCompare(b.name, 'fi'));
  // }});

  // TODO: Add helper methods for template
  // protected onItemClick(item: ItemDTO): void {{
  //   this.itemClick.emit(item);
  // }}
}}
'''

    # HTML content
    html_content = '''<!-- TODO: Implement presentational template -->
<!-- Example list template:

@for (item of sortedItems(); track item.id) {
  <div class="item-row" (click)="onItemClick(item)">
    <span>{{ item.name }}</span>
    @if (showActions()) {
      <div class="item-actions">
        <button matButton class="only-icon" (click)="deleteClick.emit(item.id); $event.stopPropagation()">
          <mat-icon>delete</mat-icon>
        </button>
      </div>
    }
  </div>
} @empty {
  <shared-empty-state
    icon="folder_open"
    title="Ei tietoja"
    message="Ei näytettäviä kohteita."
  >
  </shared-empty-state>
}

-->
'''

    # Write files
    ts_file.write_text(ts_content)
    html_file.write_text(html_content)

    print(f"Created presentational component:")
    print(f"  {ts_file}")
    print(f"  {html_file}")
    print()
    print(f"Component: {full_component_name}")
    print(f"Selector: {selector}")
    print()
    print("TODO:")
    print("  1. Import DTOs from @api/index")
    print("  2. Define inputs using input() function")
    print("  3. Define outputs using output() function")
    print("  4. Add computed signals from inputs")
    print("  5. Implement HTML template")
    print("  6. Export from feature's components/index.ts")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python .claude/skills/frontend-component/scripts/init_frontend_component.py <feature> <component-name>")
        print("Example: python .claude/skills/frontend-component/scripts/init_frontend_component.py accounting posting-list-viewer")
        sys.exit(1)

    feature = sys.argv[1]
    component_name = sys.argv[2]

    create_presentational_component(feature, component_name)
