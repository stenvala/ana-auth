import { Component, ChangeDetectionStrategy, input, output } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'shared-empty-state',

  imports: [MatIconModule, MatButtonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-empty-state.component.html',
  styleUrl: './shared-empty-state.component.scss',
})
export class SharedEmptyStateComponent {
  icon = input<string>('');
  title = input<string>('Ei tietoja');
  message = input<string>('');
  actionLabel = input<string>('');
  size = input<'default' | 'small'>('default');
  actionClick = output<void>();

  onAction(): void {
    this.actionClick.emit();
  }
}
