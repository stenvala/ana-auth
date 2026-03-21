import { computed, Injectable, signal } from '@angular/core';
import {
  Router,
  Event,
  ActivatedRoute,
  ActivationEnd,
  Params,
  ActivationStart,
} from '@angular/router';

export interface RouteData {
  hideNavbar?: boolean;
}

@Injectable({ providedIn: 'root' })
export class CoreNavService {
  currentPath = signal<string>('');
  currentPathTemplate = computed(() => {
    const reverseRouteParamMap = Object.keys(this.routeParamMap()).reduce(
      (acc, key) => {
        acc[this.routeParamMap()[key]] = '/:' + key;
        return acc;
      },
      {} as Record<string, string>,
    );
    const template = this.getPath(this.currentPath(), reverseRouteParamMap, '/');
    return template.length > 0 ? template.substring(1) : '';
  });

  routeParamMap = signal<Record<string, string>>({});
  queryParamMap = signal<Record<string, string>>({});
  routeData = signal<RouteData>({});

  private pendingQpUpdates: Record<string, string> = {};

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
  ) {
    router.events.subscribe((i: Event) => {
      if (i instanceof ActivationEnd || i instanceof ActivationStart) {
        this.routeParamMap.set(i.snapshot.params);
        this.queryParamMap.set(i.snapshot.queryParams);
        this.routeData.set(i.snapshot.data as RouteData);
      }
      if ('url' in i && i.url !== this.currentPath()) {
        this.currentPath.set(i.url);
      }
    });
  }

  goto(
    path: string,
    params?: { [key: string]: string | number },
    queryParams?: { [key: string]: string },
  ) {
    this.router.navigate([this.getPath(path, params)], {
      queryParams,
    });
  }

  getPath(path: string, params?: { [key: string]: string | number }, prefix: string = ':') {
    if (params) {
      Object.keys(params).forEach((key) => {
        path = path.replace(`${prefix}${key}`, params[key].toString());
      });
    }
    Object.keys(this.routeParamMap()).forEach((key) => {
      path = path.replace(`${prefix}${key}`, this.routeParamMap()[key]);
    });
    return path;
  }

  setQueryParams(qp: Params, immediate = false) {
    this.pendingQpUpdates = Object.assign(this.pendingQpUpdates, qp);
    const fun = () => {
      if (Object.keys(this.pendingQpUpdates).length === 0) {
        return;
      }
      this.router.navigate([], {
        relativeTo: this.activatedRoute,
        queryParams: this.pendingQpUpdates,
        queryParamsHandling: 'merge',
      });
      this.pendingQpUpdates = {};
    };
    if (immediate) {
      fun();
    }
    setTimeout(fun, 50);
  }
}
