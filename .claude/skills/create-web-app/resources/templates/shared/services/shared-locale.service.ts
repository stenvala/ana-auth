import { Injectable } from '@angular/core';

export enum DateFormat {
  Short = 'short',
  Long = 'long',
  DateTime = 'datetime',
  Full = 'full',
}

export enum TimeFormat {
  Short = 'short',
  Long = 'long',
}

export enum CurrencyFormat {
  Standard = 'standard',
  Symbol = 'symbol',
  Plain = 'plain',
}

@Injectable({
  providedIn: 'root',
})
export class SharedLocaleService {
  private readonly locale = 'fi-FI';

  formatDate(
    date: Date | string | number | null | undefined,
    format: DateFormat = DateFormat.Short,
  ): string {
    if (date === null || date === undefined) return '';

    let d: Date;
    if (typeof date === 'number') {
      d = new Date(date * 1000);
    } else if (typeof date === 'string') {
      d = new Date(date);
    } else {
      d = date;
    }

    if (isNaN(d.getTime())) return '';

    const options: Intl.DateTimeFormatOptions = this.getDateFormatOptions(format);
    return d.toLocaleDateString(this.locale, options);
  }

  formatTime(
    date: Date | string | number | null | undefined,
    format: TimeFormat = TimeFormat.Short,
  ): string {
    if (date === null || date === undefined) return '';

    let d: Date;
    if (typeof date === 'number') {
      d = new Date(date * 1000);
    } else if (typeof date === 'string') {
      d = new Date(date);
    } else {
      d = date;
    }

    if (isNaN(d.getTime())) return '';

    const options: Intl.DateTimeFormatOptions =
      format === TimeFormat.Long
        ? { hour: '2-digit', minute: '2-digit', second: '2-digit' }
        : { hour: '2-digit', minute: '2-digit' };

    return d.toLocaleTimeString(this.locale, options);
  }

  formatNumber(value: number | string | null | undefined, decimals: number = 0): string {
    if (value === null || value === undefined || value === '') return '';

    const num = typeof value === 'string' ? parseFloat(value) : value;

    if (isNaN(num)) return '';

    return num.toLocaleString(this.locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }

  formatCurrency(
    value: number | string | null | undefined,
    format: CurrencyFormat = CurrencyFormat.Symbol,
    currency: string = 'EUR',
  ): string {
    if (value === null || value === undefined || value === '') return '';

    const num = typeof value === 'string' ? parseFloat(value) : value;

    if (isNaN(num)) return '';

    if (format === CurrencyFormat.Plain) {
      return num.toFixed(2);
    }

    const options: Intl.NumberFormatOptions = {
      style: 'currency',
      currency,
      currencyDisplay: format === CurrencyFormat.Symbol ? 'symbol' : 'code',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    };

    return num.toLocaleString(this.locale, options);
  }

  parseNumber(value: string | null | undefined): number {
    if (!value) return NaN;

    const normalized = value.replace(/\s/g, '').replace(',', '.');
    return parseFloat(normalized);
  }

  parseDate(value: string | null | undefined): Date | null {
    if (!value) return null;

    const parts = value.split('.');
    if (parts.length === 3) {
      const day = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1;
      const year = parseInt(parts[2], 10);

      const date = new Date(year, month, day);
      if (!isNaN(date.getTime())) {
        return date;
      }
    }

    const date = new Date(value);
    return isNaN(date.getTime()) ? null : date;
  }

  private getDateFormatOptions(format: DateFormat): Intl.DateTimeFormatOptions {
    switch (format) {
      case DateFormat.Long:
        return { day: 'numeric', month: 'long', year: 'numeric' };
      case DateFormat.DateTime:
        return {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        };
      case DateFormat.Full:
        return { weekday: 'long', day: 'numeric', month: 'numeric', year: 'numeric' };
      case DateFormat.Short:
      default:
        return { day: '2-digit', month: '2-digit', year: 'numeric' };
    }
  }
}
