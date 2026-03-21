import { Pipe, PipeTransform, inject } from '@angular/core';
import { SharedLocaleService } from '../services/shared-locale.service';

@Pipe({
  name: 'sharedNumberFormat',
})
export class SharedNumberFormatPipe implements PipeTransform {
  private readonly locale = inject(SharedLocaleService);

  transform(value: number | string | null | undefined, decimals: number = 0): string {
    return this.locale.formatNumber(value, decimals);
  }
}
