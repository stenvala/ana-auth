import { Component, ChangeDetectionStrategy, input, computed } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

export type BannerType = 'error' | 'info' | 'warning' | 'success';

@Component({
  selector: 'shared-banner',

  imports: [MatIconModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-banner.component.html',
  styleUrl: './shared-banner.component.scss',
})
export class SharedBannerComponent {
  type = input<BannerType>('info');
  title = input<string>('');
  message = input<string>('');

  protected readonly iconName = computed(() => {
    switch (this.type()) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'success':
        return 'check_circle';
      case 'info':
      default:
        return 'info';
    }
  });
}
