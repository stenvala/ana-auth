#!/usr/bin/env python3
"""
Initialize dummy Angular service and store files.

Usage:
    python .claude/skills/frontend-service/scripts/init_frontend_service.py <feature> <entity-name>

Example:
    python .claude/skills/frontend-service/scripts/init_frontend_service.py accounting document

This creates:
    src/ui/src/app/features/accounting/services/
        accounting-document.service.ts
        accounting-document.store.ts
"""

import os
import sys
from pathlib import Path


def to_pascal_case(kebab_name: str) -> str:
    """Convert kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in kebab_name.split("-"))


def create_service_files(feature: str, entity_name: str):
    """Create service and state service files with minimal skeleton."""

    feature_pascal = to_pascal_case(feature)
    entity_pascal = to_pascal_case(entity_name)

    # Paths
    base_path = Path("src/ui/src/app/features") / feature / "services"
    service_file = base_path / f"{feature}-{entity_name}.service.ts"
    state_file = base_path / f"{feature}-{entity_name}.store.ts"

    # Create directory
    base_path.mkdir(parents=True, exist_ok=True)

    # State service content
    state_content = f'''import {{ Injectable, Signal, computed }} from '@angular/core';
import {{ ListStore, ObjectStore }} from '@core/stores';
// TODO: Import DTOs from @api/index
// import {{ {entity_pascal}DTO }} from '@api/index';

// Placeholder type - replace with actual DTO
type {entity_pascal}DTO = {{ id: string }};

@Injectable({{ providedIn: 'root' }})
export class {feature_pascal}{entity_pascal}Store {{
  /**
   * Normalized entity store: id -> {entity_pascal}DTO
   * Single source of truth for all items
   */
  readonly {entity_name.replace('-', '')}Entities = new ObjectStore<{entity_pascal}DTO>();

  /**
   * Search result store: serialized criteria -> {{ id: string }}[]
   * Stores only item IDs for each search criteria
   */
  readonly searchResults = new ListStore<{{ id: string }}>();

  /**
   * Get items for a search criteria key.
   * Returns computed signal that joins IDs to entities.
   */
  get{entity_pascal}sBySearchKey(searchKey: string): Signal<{entity_pascal}DTO[] | null> {{
    return computed(() => {{
      const ids = this.searchResults.get(searchKey)();
      if (ids === null) return null;
      return ids
        .map(item => this.{entity_name.replace('-', '')}Entities.get(item.id)())
        .filter((doc): doc is {entity_pascal}DTO => !!doc);
    }});
  }}

  /**
   * Check if a search key exists in results
   */
  has(searchKey: string): boolean {{
    return this.searchResults.isInitialized(searchKey);
  }}

  /**
   * Store items and their search result IDs
   */
  setSearchResults(searchKey: string, items: {entity_pascal}DTO[]): void {{
    const idList = items.map(item => {{
      this.{entity_name.replace('-', '')}Entities.set(item.id, item);
      return {{ id: item.id }};
    }});
    this.searchResults.set(searchKey, idList);
  }}

  /**
   * Remove an item from entity store and all search results
   */
  remove{entity_pascal}(id: string): void {{
    this.{entity_name.replace('-', '')}Entities.remove(id);

    this.searchResults.getAllKeys().forEach(searchKey => {{
      const idList = this.searchResults.get(searchKey)();
      if (idList) {{
        const filtered = idList.filter(i => i.id !== id);
        if (filtered.length !== idList.length) {{
          this.searchResults.set(searchKey, filtered);
        }}
      }}
    }});
  }}

  clearAll(): void {{
    this.{entity_name.replace('-', '')}Entities.clear();
    this.searchResults.clear();
  }}

  clearSearchResults(): void {{
    this.searchResults.clear();
  }}
}}
'''

    # Service content
    service_content = f'''import {{ Injectable, inject, Signal, untracked }} from '@angular/core';
import {{ firstValueFrom }} from 'rxjs';
// TODO: Import API service and DTOs from @api/index
// import {{
//   {entity_pascal}DTO,
//   {entity_pascal}CreateDTO,
//   {entity_pascal}UpdateDTO,
//   Private{entity_pascal}ApiService,
// }} from '@api/index';
import {{ {feature_pascal}{entity_pascal}Store }} from './{feature}-{entity_name}.store';
import {{ SharedNotificationService }} from '@shared/index';

export interface {entity_pascal}SearchCriteria {{
  // TODO: Define search criteria
  fiscalYearId: string | null;
}}

// Placeholder types - replace with actual DTOs
type {entity_pascal}DTO = {{ id: string }};
type {entity_pascal}CreateDTO = {{}};
type {entity_pascal}UpdateDTO = {{}};

@Injectable({{ providedIn: 'root' }})
export class {feature_pascal}{entity_pascal}Service {{
  // TODO: Inject API service
  // private readonly api = inject(Private{entity_pascal}ApiService);
  private readonly state = inject({feature_pascal}{entity_pascal}Store);
  private readonly notification = inject(SharedNotificationService);

  /**
   * Get a single item by ID.
   */
  getById(id: string): Signal<{entity_pascal}DTO | null> {{
    const item = this.state.{entity_name.replace('-', '')}Entities.get(id);
    if (!item()) {{
      untracked(() => this.loadById(id));
    }}
    return item;
  }}

  async loadById(id: string, refresh = false): Promise<{entity_pascal}DTO | null> {{
    const current = this.state.{entity_name.replace('-', '')}Entities.get(id)();
    if (!refresh && current) {{
      return current;
    }}
    // TODO: Implement API call
    // const response = await firstValueFrom(this.api.get{entity_pascal}(id));
    // this.state.{entity_name.replace('-', '')}Entities.set(response.id, response);
    // return response;
    return null;
  }}

  /**
   * Get items matching search criteria.
   */
  getSearchResults(criteria: {entity_pascal}SearchCriteria): Signal<{entity_pascal}DTO[] | null> {{
    const searchKey = this.serializeCriteria(criteria);
    if (!this.state.has(searchKey)) {{
      untracked(() => this.loadSearchResults(criteria, searchKey));
    }}
    return this.state.get{entity_pascal}sBySearchKey(searchKey);
  }}

  private serializeCriteria(criteria: {entity_pascal}SearchCriteria): string {{
    return JSON.stringify({{
      fiscalYearId: criteria.fiscalYearId,
      // TODO: Add other criteria fields
    }});
  }}

  async loadSearchResults(
    criteria: {entity_pascal}SearchCriteria,
    searchKey: string = '',
    refresh = false
  ): Promise<{entity_pascal}DTO[]> {{
    if (!criteria.fiscalYearId) {{
      throw new Error('Fiscal year must be provided');
    }}
    if (!searchKey) {{
      searchKey = this.serializeCriteria(criteria);
    }}
    if (!refresh && this.state.has(searchKey)) {{
      return this.state.get{entity_pascal}sBySearchKey(searchKey)()!;
    }}
    // TODO: Implement API call
    // const response = await firstValueFrom(this.api.list{entity_pascal}s(criteria.fiscalYearId));
    // this.state.setSearchResults(searchKey, response.items);
    // return response.items;
    return [];
  }}

  invalidateSearchCache(): void {{
    this.state.clearSearchResults();
  }}

  async create(dto: {entity_pascal}CreateDTO): Promise<{entity_pascal}DTO | null> {{
    try {{
      // TODO: Implement API call
      // const result = await firstValueFrom(this.api.create{entity_pascal}(dto));
      // this.state.{entity_name.replace('-', '')}Entities.set(result.id, result);
      // this.state.clearSearchResults();
      this.notification.success('Luotu onnistuneesti');
      return null; // TODO: Return result
    }} catch (error: any) {{
      const message = error?.error?.detail?.message || 'Luonti epäonnistui';
      this.notification.error(message);
      return null;
    }}
  }}

  async update(id: string, dto: {entity_pascal}UpdateDTO): Promise<{entity_pascal}DTO | null> {{
    try {{
      // TODO: Implement API call
      // const result = await firstValueFrom(this.api.update{entity_pascal}(id, dto));
      // this.state.{entity_name.replace('-', '')}Entities.set(result.id, result);
      this.notification.success('Päivitetty onnistuneesti');
      return null; // TODO: Return result
    }} catch (error: any) {{
      const message = error?.error?.detail?.message || 'Päivitys epäonnistui';
      this.notification.error(message);
      return null;
    }}
  }}

  async delete(id: string): Promise<boolean> {{
    try {{
      // TODO: Implement API call
      // await firstValueFrom(this.api.delete{entity_pascal}(id));
      this.state.remove{entity_pascal}(id);
      this.notification.success('Poistettu onnistuneesti');
      return true;
    }} catch (error: any) {{
      const message = error?.error?.detail?.message || 'Poisto epäonnistui';
      this.notification.error(message);
      return false;
    }}
  }}
}}
'''

    # Write files
    state_file.write_text(state_content)
    service_file.write_text(service_content)

    print(f"Created service files:")
    print(f"  {state_file}")
    print(f"  {service_file}")
    print()
    print(f"Store: {feature_pascal}{entity_pascal}Store")
    print(f"Service: {feature_pascal}{entity_pascal}Service")
    print()
    print("TODO:")
    print("  1. Import DTOs from @api/index")
    print("  2. Import and inject API service")
    print("  3. Define SearchCriteria interface")
    print("  4. Implement API calls in all methods")
    print("  5. Export from feature's services/index.ts")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python .claude/skills/frontend-service/scripts/init_frontend_service.py <feature> <entity-name>")
        print("Example: python .claude/skills/frontend-service/scripts/init_frontend_service.py accounting document")
        sys.exit(1)

    feature = sys.argv[1]
    entity_name = sys.argv[2]

    create_service_files(feature, entity_name)
