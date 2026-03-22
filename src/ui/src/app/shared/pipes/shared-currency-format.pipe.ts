import { Pipe, PipeTransform, inject } from '@angular/core';
import { SharedLocaleService, CurrencyFormat } from '../services/shared-locale.service';

@Pipe({
  name: 'sharedCurrencyFormat',
})
export class SharedCurrencyFormatPipe implements PipeTransform {
  private readonly locale = inject(SharedLocaleService);

  transform(
    value: number | string | null | undefined,
    format: keyof typeof CurrencyFormat = 'Symbol',
  ): string {
    return this.locale.formatCurrency(value, CurrencyFormat[format]);
  }
}
