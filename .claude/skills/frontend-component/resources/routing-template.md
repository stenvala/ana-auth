# Routing Template

## Path Constants

Add to `src/ui/src/app/core/constants/paths.ts`:

```typescript
FEATURE: {
  LIST: {
    path: "pri/group/:privateGroupId/features",
  },
  DETAIL: {
    path: "pri/group/:privateGroupId/features/:featureId",
  },
  EDIT: {
    path: "pri/group/:privateGroupId/features/:featureId/edit",
  },
  CREATE: {
    path: "pri/group/:privateGroupId/features/create",
  },
},
```

## Route Configuration

Add to `src/ui/src/app/app.routes.ts`:

```typescript
import { RouteFeatureListComponent } from './features/feature/components/route-feature-list/route-feature-list.component';
import { RouteFeatureDetailComponent } from './features/feature/components/route-feature-detail/route-feature-detail.component';
import { RouteFeatureEditorComponent } from './features/feature/components/route-feature-editor/route-feature-editor.component';

// In routes array:
{
  path: PATHS.PRIVATE.FEATURE.LIST.path,
  component: RouteFeatureListComponent,
  canActivate: [authGuard, translationsGuard],
},
{
  path: PATHS.PRIVATE.FEATURE.DETAIL.path,
  component: RouteFeatureDetailComponent,
  canActivate: [authGuard, translationsGuard],
},
{
  path: PATHS.PRIVATE.FEATURE.EDIT.path,
  component: RouteFeatureEditorComponent,
  canActivate: [authGuard, translationsGuard],
},
{
  path: PATHS.PRIVATE.FEATURE.CREATE.path,
  component: RouteFeatureEditorComponent,
  canActivate: [authGuard, translationsGuard],
},
```

## Navigation Usage

```typescript
// In component:
import { CoreNavService } from '@core/services';
import { PATHS } from '@core/constants';

private nav = inject(CoreNavService);

// Navigate to list
this.nav.goto(PATHS.PRIVATE.FEATURE.LIST.path, {
  privateGroupId: groupId,
});

// Navigate to detail
this.nav.goto(PATHS.PRIVATE.FEATURE.DETAIL.path, {
  privateGroupId: groupId,
  featureId: feature.id,
});

// Get route params
private featureId = computed(() => this.nav.routeParamMap()['featureId'] || null);
```
