import { Component, computed, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CoreNavService } from '@core/services/core-nav.service';
import { CoreNavbarComponent } from '@core/components/core-navbar/core-navbar.component';

@Component({
  selector: 'app-root',

  imports: [RouterOutlet, CoreNavbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  private readonly navService = inject(CoreNavService);
  protected readonly hideNavbar = computed(() => this.navService.routeData().hideNavbar ?? false);

  // TODO: Add authentication state when auth service is implemented
  // protected readonly isAuthenticated = this.authService.isAuthenticated;
}
