# Angular Core Foundation

Copy all files from `references/templates/core/` to `src/ui/src/app/core/`.

## Files Included

### Stores (signal-based state management base classes)
- `stores/value.store.ts` - Single value store
- `stores/object.store.ts` - Key-value object store
- `stores/list.store.ts` - List store with item management
- `stores/list-store-with-object.store.ts` - Combined list + object store
- `stores/index.ts` - Barrel export

### Services
- `services/core-nav.service.ts` - Navigation/routing service with signals
- `services/index.ts` - Barrel export

### Constants (empty templates)
- `constants/paths.ts` - Route paths placeholder (populate per project)
- `constants/index.ts` - Barrel export

### Guards (empty template)
- `guards/index.ts` - Placeholder for route guards

### Components (empty templates)
- `components/core-navbar/` - Minimal navbar placeholder (ts, html, scss)
- `components/index.ts` - Barrel export

### Module & Barrel
- `core.module.ts` - Core NgModule (CommonModule, FormsModule, RouterModule, MarkdownModule)
- `index.ts` - Root barrel export
