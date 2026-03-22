import {
  Component,
  ChangeDetectionStrategy,
  input,
  output,
  OnInit,
  OnDestroy,
  signal,
  effect,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { Subject, debounceTime, distinctUntilChanged, takeUntil } from 'rxjs';

@Component({
  selector: 'shared-search-input',

  imports: [FormsModule, MatFormFieldModule, MatInputModule, MatIconModule, MatButtonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './shared-search-input.component.html',
  styleUrl: './shared-search-input.component.scss',
})
export class SharedSearchInputComponent implements OnInit, OnDestroy {
  placeholder = input<string>('Hae...');
  debounceMs = input<number>(300);
  initialValue = input<string>('');

  searchChange = output<string>();

  readonly value = signal('');

  private readonly input$ = new Subject<string>();
  private readonly destroy$ = new Subject<void>();

  constructor() {
    effect(() => {
      const initial = this.initialValue();
      if (initial) {
        this.value.set(initial);
      }
    });
  }

  ngOnInit(): void {
    this.input$
      .pipe(debounceTime(this.debounceMs()), distinctUntilChanged(), takeUntil(this.destroy$))
      .subscribe((value) => {
        this.searchChange.emit(value);
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onInput(value: string): void {
    this.value.set(value);
    this.input$.next(value);
  }

  clear(): void {
    this.value.set('');
    this.input$.next('');
  }
}
