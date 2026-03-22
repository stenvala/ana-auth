import { Component, ChangeDetectionStrategy, inject } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { SharedLoadingService } from '../../services/shared-loading.service';

@Component({
  selector: 'shared-loading-overlay',

  imports: [MatProgressSpinnerModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-loading-overlay.component.html',
  styleUrl: './shared-loading-overlay.component.scss',
})
export class SharedLoadingOverlayComponent {
  readonly loading = inject(SharedLoadingService);
}
