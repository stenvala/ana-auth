/**
 * Shared module - reusable, stateless components, directives, and pipes
 */
export * from './mat.module';
export * from './shared.module';

// Services
export * from './services/shared-locale.service';
export * from './services/shared-notification.service';
export * from './services/shared-loading.service';
export * from './services/shared-dialog-confirm.service';
export * from './services/shared-confirm.service';
export * from './services/shared-control-state.service';

// Pipes
export * from './pipes/shared-date-format.pipe';
export * from './pipes/shared-time-format.pipe';
export * from './pipes/shared-number-format.pipe';
export * from './pipes/shared-currency-format.pipe';

// Directives
export * from './directives/shared-loading-button.directive';

// Components
export * from './components/shared-banner/shared-banner.component';
export * from './components/shared-empty-state/shared-empty-state.component';
export * from './components/shared-loading-overlay/shared-loading-overlay.component';
export * from './components/shared-loading-state/shared-loading-state.component';
export * from './components/shared-loading-spinner/shared-loading-spinner.component';
export * from './components/shared-loading-bar/shared-loading-bar.component';
export * from './components/shared-search-input/shared-search-input.component';
export * from './components/shared-badge/shared-badge.component';
export * from './components/shared-confirm-dialog/shared-confirm-dialog.component';
