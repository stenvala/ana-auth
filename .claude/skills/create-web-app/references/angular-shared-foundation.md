# Angular Shared Foundation

Copy all files from `references/templates/shared/` to `src/ui/src/app/shared/`.

## Files Included

### Modules
- `mat.module.ts` - Material Design module with all common Material imports
- `shared.module.ts` - Shared NgModule aggregating all shared components, pipes, directives
- `index.ts` - Root barrel export for all shared exports

### Components
- `components/shared-loading-overlay/` - Full-screen loading overlay (ts, html, scss)
- `components/shared-loading-spinner/` - Inline spinner (ts, html, scss)
- `components/shared-loading-state/` - Loading with message (ts, html, scss)
- `components/shared-loading-bar/` - Progress bar (ts, html, scss)
- `components/shared-confirm-dialog/` - Confirmation dialog with static open pattern (ts, html)
- `components/shared-empty-state/` - Empty state with icon and action (ts, html, scss)
- `components/shared-banner/` - Info/warning/error/success banner (ts, html, scss)
- `components/shared-search-input/` - Debounced search input (ts, html, scss)
- `components/shared-badge/` - Colored badge component (ts, html, scss)
- `components/index.ts` - Component barrel export

### Directives
- `directives/shared-loading-button.directive.ts` - Async button with loading state and optional confirmation
- `directives/index.ts` - Barrel export

### Pipes (Finnish locale formatting)
- `pipes/shared-date-format.pipe.ts` - Date formatting
- `pipes/shared-time-format.pipe.ts` - Time formatting
- `pipes/shared-number-format.pipe.ts` - Number formatting
- `pipes/shared-currency-format.pipe.ts` - Currency formatting (EUR)
- `pipes/index.ts` - Barrel export

### Services
- `services/shared-locale.service.ts` - Finnish locale formatting (dates, times, numbers, currency)
- `services/shared-notification.service.ts` - Toast notifications via MatSnackBar
- `services/shared-loading.service.ts` - Global loading state with signal-based counter
- `services/shared-dialog-confirm.service.ts` - Dialog-based confirmations
- `services/shared-confirm.service.ts` - Inline "click-again-to-confirm" pattern
- `services/shared-control-state.service.ts` - localStorage-based form value persistence
