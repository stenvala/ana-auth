import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'shared-loading-state',

  imports: [MatProgressSpinnerModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-loading-state.component.html',
  styleUrl: './shared-loading-state.component.scss',
})
export class SharedLoadingStateComponent {
  message = input<string>('Ladataan...');
  size = input<number>(48);
}
