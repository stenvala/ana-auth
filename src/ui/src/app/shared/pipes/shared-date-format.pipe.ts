import { Pipe, PipeTransform, inject } from '@angular/core';
import { SharedLocaleService, DateFormat } from '../services/shared-locale.service';

@Pipe({
  name: 'sharedDateFormat',
})
export class SharedDateFormatPipe implements PipeTransform {
  private readonly locale = inject(SharedLocaleService);

  transform(
    value: Date | string | number | null | undefined,
    format: keyof typeof DateFormat = 'Short',
  ): string {
    return this.locale.formatDate(value, DateFormat[format]);
  }
}
