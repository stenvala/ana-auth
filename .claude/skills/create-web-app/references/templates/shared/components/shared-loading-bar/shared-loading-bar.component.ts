import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { MatProgressBarModule, ProgressBarMode } from '@angular/material/progress-bar';

@Component({
  selector: 'shared-loading-bar',

  imports: [MatProgressBarModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-loading-bar.component.html',
  styleUrl: './shared-loading-bar.component.scss',
})
export class SharedLoadingBarComponent {
  mode = input<ProgressBarMode>('indeterminate');
  value = input<number>(0);
}
