import { Pipe, PipeTransform, inject } from '@angular/core';
import { SharedLocaleService, TimeFormat } from '../services/shared-locale.service';

@Pipe({
  name: 'sharedTimeFormat',
})
export class SharedTimeFormatPipe implements PipeTransform {
  private readonly locale = inject(SharedLocaleService);

  transform(
    value: Date | string | number | null | undefined,
    format: keyof typeof TimeFormat = 'Short',
  ): string {
    return this.locale.formatTime(value, TimeFormat[format]);
  }
}
