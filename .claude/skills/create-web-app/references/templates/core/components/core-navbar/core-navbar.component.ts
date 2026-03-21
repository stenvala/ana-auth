import { Component, inject } from '@angular/core';
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/index';
import { PATHS } from '@core/constants/paths';

@Component({
  selector: 'core-navbar',

  imports: [CoreModule, MaterialModule],
  templateUrl: './core-navbar.component.html',
  styleUrl: './core-navbar.component.scss',
})
export class CoreNavbarComponent {
  protected readonly paths = PATHS;

  // TODO: Inject auth service and add navigation logic
}
