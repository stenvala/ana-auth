import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'shared-loading-spinner',

  imports: [MatProgressSpinnerModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-loading-spinner.component.html',
  styleUrl: './shared-loading-spinner.component.scss',
})
export class SharedLoadingSpinnerComponent {
  size = input<number>(24);
}
