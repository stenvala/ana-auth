# Shared Component Template

## Application-Wide Reusable Components

Shared components are reusable across the entire application. They are located in
`src/ui/src/app/shared/components/` and exported via `SharedModule`.

**IMPORTANT**: Shared components must NOT import `SharedModule` to avoid circular dependencies.
Only import `[CoreModule, MaterialModule]`.

```typescript
import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  computed,
} from "@angular/core";
import { CoreModule } from "@core/modules";
import { MaterialModule } from "@shared/material";

/**
 * Shared loading state component
 *
 * Displays a loading spinner with optional message.
 * Used across the application for consistent loading UX.
 */
@Component({
  selector: "shared-loading-state",
  // IMPORTANT: No SharedModule - only CoreModule and MaterialModule
  imports: [CoreModule, MaterialModule],
  templateUrl: "./shared-loading-state.component.html",
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SharedLoadingStateComponent {
  // Component inputs
  message = input<string>("Loading...");
  size = input<"small" | "medium" | "large">("medium");

  // Computed properties
  spinnerDiameter = computed(() => {
    const sizeMap = { small: 24, medium: 40, large: 64 };
    return sizeMap[this.size()];
  });
}
```

## Template Pattern

**IMPORTANT**: All interactive elements, rendered values, and key content must have `data-test-id` attributes for E2E testing. See SKILL.md for full naming convention. Use the component's selector prefix for `data-test-id` names (e.g., `shared-loading-state-spinner`, `shared-loading-state-message`).

```html
<div class="loading-state" data-test-id="loading-state">
  <mat-spinner [diameter]="spinnerDiameter()"></mat-spinner>
  @if (message()) {
  <p class="loading-message" data-test-id="loading-message">{{ message() }}</p>
  }
</div>
```

## Registration in SharedModule

After creating the component, register it in `shared.module.ts`:

```typescript
// src/ui/src/app/shared/shared.module.ts
import { SharedLoadingStateComponent } from './components/shared-loading-state/shared-loading-state.component';

const SHARED_COMPONENTS = [
  // ... existing components
  SharedLoadingStateComponent,
];
```

## Key Differences from Feature Presentational Components

| Aspect | Feature Component | Shared Component |
|--------|-------------------|------------------|
| Location | `features/<feature>/components/` | `shared/components/shared-<name>/` |
| Prefix | `<feature>-` or descriptive | `shared-` always |
| Imports | `[CoreModule, MaterialModule, SharedModule]` | `[CoreModule, MaterialModule]` only |
| Export | Feature's `components/index.ts` | `SHARED_COMPONENTS` in `shared.module.ts` |
| Available via | Direct import | `SharedModule` import |

## Naming Convention

- Folder: `shared-<name>/` (e.g., `shared-pdf-viewer/`)
- Files: `shared-<name>.component.ts`, `shared-<name>.component.html`
- Class: `Shared<Name>Component` (e.g., `SharedPdfViewerComponent`)
- Selector: `shared-<name>` (e.g., `shared-pdf-viewer`)

## Examples of Shared Components

- `shared-empty-state` - Empty content placeholder
- `shared-loading-state` - Loading indicator with message
- `shared-loading-spinner` - Simple spinner
- `shared-loading-overlay` - Full-screen loading overlay
- `shared-pdf-viewer` - PDF document viewer
- `shared-search-input` - Search input field
- `shared-resizable-split-panel` - Resizable split layout
