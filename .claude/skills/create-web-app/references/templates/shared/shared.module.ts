import { NgModule } from '@angular/core';

// Components
import { SharedEmptyStateComponent } from './components/shared-empty-state/shared-empty-state.component';
import { SharedLoadingOverlayComponent } from './components/shared-loading-overlay/shared-loading-overlay.component';
import { SharedLoadingStateComponent } from './components/shared-loading-state/shared-loading-state.component';
import { SharedLoadingSpinnerComponent } from './components/shared-loading-spinner/shared-loading-spinner.component';
import { SharedLoadingBarComponent } from './components/shared-loading-bar/shared-loading-bar.component';
import { SharedSearchInputComponent } from './components/shared-search-input/shared-search-input.component';
import { SharedBadgeComponent } from './components/shared-badge/shared-badge.component';
import { SharedBannerComponent } from './components/shared-banner/shared-banner.component';

// Pipes
import { SharedDateFormatPipe } from './pipes/shared-date-format.pipe';
import { SharedTimeFormatPipe } from './pipes/shared-time-format.pipe';
import { SharedNumberFormatPipe } from './pipes/shared-number-format.pipe';
import { SharedCurrencyFormatPipe } from './pipes/shared-currency-format.pipe';

// Directives
import { SharedLoadingButtonDirective } from './directives/shared-loading-button.directive';

const SHARED_COMPONENTS = [
  SharedEmptyStateComponent,
  SharedLoadingOverlayComponent,
  SharedLoadingStateComponent,
  SharedLoadingSpinnerComponent,
  SharedLoadingBarComponent,
  SharedSearchInputComponent,
  SharedBadgeComponent,
  SharedBannerComponent,
];

const SHARED_PIPES = [
  SharedDateFormatPipe,
  SharedTimeFormatPipe,
  SharedNumberFormatPipe,
  SharedCurrencyFormatPipe,
];

const SHARED_DIRECTIVES = [SharedLoadingButtonDirective];

@NgModule({
  imports: [...SHARED_COMPONENTS, ...SHARED_PIPES, ...SHARED_DIRECTIVES],
  exports: [...SHARED_COMPONENTS, ...SHARED_PIPES, ...SHARED_DIRECTIVES],
})
export class SharedModule {}
