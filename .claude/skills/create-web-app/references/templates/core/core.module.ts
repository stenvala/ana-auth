import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { RouterModule, RouterLink } from '@angular/router';
import { MarkdownModule } from 'ngx-markdown';

const CORE_MODULES = [
  CommonModule,
  ReactiveFormsModule,
  FormsModule,
  RouterModule,
  RouterLink,
  MarkdownModule,
];

@NgModule({
  imports: [...CORE_MODULES],
  exports: [...CORE_MODULES],
})
export class CoreModule {}
