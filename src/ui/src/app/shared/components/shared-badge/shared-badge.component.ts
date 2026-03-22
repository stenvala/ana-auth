import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Shared badge component for consistent badge styling across the application.
 *
 * Usage with color:
 * <shared-badge [color]="'success'" [value]="'Active'" />
 *
 * Usage with custom workflow color:
 * <shared-badge [customColor]="stage.color" [value]="stage.name" />
 */
@Component({
  selector: 'shared-badge',

  imports: [CommonModule],
  templateUrl: './shared-badge.component.html',
  styleUrl: './shared-badge.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SharedBadgeComponent {
  readonly color = input<string>();
  readonly badgeClass = input<string>();
  readonly customColor = input<string>();
  readonly value = input.required<string>();
  readonly size = input<'sm' | 'md' | 'lg'>('md');
  readonly showDot = input<boolean>(false);

  protected readonly badgeClasses = computed(() => {
    const classes: string[] = ['shared-badge'];

    const colorValue = this.color() || this.badgeClass();

    if (colorValue) {
      classes.push(`shared-badge--${colorValue}`);
    }

    const sizeValue = this.size();
    if (sizeValue !== 'md') {
      classes.push(`shared-badge--${sizeValue}`);
    }

    return classes.join(' ');
  });
}
