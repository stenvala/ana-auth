import { Component } from '@angular/core';
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/index';

@Component({
  selector: 'core-navbar',
  imports: [CoreModule, MaterialModule],
  templateUrl: './core-navbar.component.html',
  styleUrl: './core-navbar.component.scss',
})
export class CoreNavbarComponent {}
