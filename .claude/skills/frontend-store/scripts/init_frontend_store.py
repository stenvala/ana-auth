#!/usr/bin/env python3
"""
Initialize a dummy Angular store file.

Usage:
    python .claude/skills/frontend-store/scripts/init_frontend_store.py <feature> <entity-name>

Example:
    python .claude/skills/frontend-store/scripts/init_frontend_store.py accounting document

This creates:
    src/ui/src/app/features/accounting/services/
        accounting-document.store.ts
"""

import os
import sys
from pathlib import Path


def to_pascal_case(kebab_name: str) -> str:
    """Convert kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in kebab_name.split("-"))


def create_store_file(feature: str, entity_name: str):
    """Create state service file with minimal skeleton."""

    feature_pascal = to_pascal_case(feature)
    entity_pascal = to_pascal_case(entity_name)

    # Paths
    base_path = Path("src/ui/src/app/features") / feature / "services"
    state_file = base_path / f"{feature}-{entity_name}.store.ts"

    # Create directory
    base_path.mkdir(parents=True, exist_ok=True)

    # State service content
    state_content = f'''import {{ Injectable, Signal, computed }} from '@angular/core';
import {{ ListStore, ObjectStore }} from '@core/stores';
// TODO: Import DTOs from @api/index
// import {{ {entity_pascal}DTO, {entity_pascal}SummaryDTO }} from '@api/index';

// Placeholder types - replace with actual DTOs
type {entity_pascal}DTO = {{ id: string }};
type {entity_pascal}SummaryDTO = {{ id: string; name: string }};

@Injectable({{ providedIn: 'root' }})
export class {feature_pascal}{entity_pascal}Store {{
  /**
   * LIST STORE: Contains summary objects for list views.
   * - Keyed by search criteria (e.g., fiscalYearId, or 'all')
   * - Contains {entity_pascal}SummaryDTO which is a subset of {entity_pascal}DTO
   * - Used by list components to display tables/cards
   */
  readonly listItemsStore = new ListStore<{entity_pascal}SummaryDTO>();

  /**
   * OBJECT STORE: Contains full objects for detail views.
   * - Keyed by item ID
   * - Contains {entity_pascal}DTO with all fields and relationships
   * - Used by detail/edit components
   */
  readonly itemStore = new ObjectStore<{entity_pascal}DTO>();

  /**
   * Get list items for a search key.
   * Returns summary DTOs suitable for list views.
   */
  getListItems(searchKey: string): Signal<{entity_pascal}SummaryDTO[] | null> {{
    return this.listItemsStore.get(searchKey);
  }}

  /**
   * Get full item by ID.
   * Returns complete DTO for detail views.
   */
  getItem(id: string): Signal<{entity_pascal}DTO | null> {{
    return this.itemStore.get(id);
  }}

  /**
   * Store list items from search results.
   */
  setListItems(searchKey: string, items: {entity_pascal}SummaryDTO[]): void {{
    this.listItemsStore.set(searchKey, items);
  }}

  /**
   * Store a full item.
   * NOTE: When updating an item, you may need to also update or clear
   * the listItemsStore depending on your use case.
   */
  setItem(id: string, item: {entity_pascal}DTO): void {{
    this.itemStore.set(id, item);
    // Option A: Clear list caches to force refresh
    // this.listItemsStore.clear();
  }}

  /**
   * Remove an item from both stores.
   */
  removeItem(id: string): void {{
    this.itemStore.remove(id);

    // Remove from all list caches
    this.listItemsStore.getAllKeys().forEach(searchKey => {{
      const items = this.listItemsStore.get(searchKey)();
      if (items) {{
        const filtered = items.filter(i => i.id !== id);
        if (filtered.length !== items.length) {{
          this.listItemsStore.set(searchKey, filtered);
        }}
      }}
    }});
  }}

  clearAll(): void {{
    this.listItemsStore.clear();
    this.itemStore.clear();
  }}

  /**
   * Clear list caches only (items remain for detail views).
   */
  clearListCaches(): void {{
    this.listItemsStore.clear();
  }}
}}
'''

    # Write file
    state_file.write_text(state_content)

    print(f"Created store file:")
    print(f"  {state_file}")
    print()
    print(f"Store: {feature_pascal}{entity_pascal}Store")
    print()
    print("TODO:")
    print("  1. Import DTOs from @api/index")
    print("  2. Replace placeholder types with actual DTOs")
    print("  3. Adjust store types based on your data needs:")
    print("     - Pattern 1: ListStore (Summary) + ObjectStore (Full) - current template")
    print("     - Pattern 2: ID List + Entity Store (Normalized)")
    print("     - Pattern 3: Simple ListStore")
    print("  4. Export from feature's services/index.ts")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python .claude/skills/frontend-store/scripts/init_frontend_store.py <feature> <entity-name>")
        print("Example: python .claude/skills/frontend-store/scripts/init_frontend_store.py accounting document")
        sys.exit(1)

    feature = sys.argv[1]
    entity_name = sys.argv[2]

    create_store_file(feature, entity_name)
