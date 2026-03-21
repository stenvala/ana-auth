# Angular 21 Setup Reference

## 1. Create .nvmrc File

Create `.nvmrc` in the project root to specify Node.js version:

```
20.19
```

This ensures consistent Node.js version across development environments using nvm.

## 2. Initialize Angular Project

```bash
# Use correct Node.js version (if using nvm)
nvm use

# Create Angular project with routing and SCSS
ng new <project-name> --routing --style=scss --skip-git

# Move to src/ui location
mkdir -p src
mv <project-name> src/ui

# Navigate to UI directory
cd src/ui

# Add Angular Material
ng add @angular/material
```

## 3. Create Folder Structure

The foundation files (step 5) will create the full directory structure. At minimum, ensure these directories exist under `src/ui/src/app/`:

```
app/
├── core/          # Populated by angular-core-foundation.md
├── shared/        # Populated by angular-shared-foundation.md
└── features/      # Feature modules go here (empty at setup)
```

## 4. TypeScript Configuration

Update `src/ui/tsconfig.json` with path aliases:

```json
{
  "compileOnSave": false,
  "compilerOptions": {
    "outDir": "./dist/out-tsc",
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "sourceMap": true,
    "declaration": false,
    "experimentalDecorators": true,
    "moduleResolution": "bundler",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"],
    "baseUrl": "./",
    "typeRoots": ["node_modules/@types"],
    "paths": {
      "@core/*": ["src/app/core/*"],
      "@shared/*": ["src/app/shared/*"],
      "@features/*": ["src/app/features/*"]
    }
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

## 5. Install Foundation Files

After Angular CLI scaffolding, install the foundation template files. See:

- `angular-core-foundation.md` - Core module, stores, nav service, interceptor, navbar, paths
- `angular-shared-foundation.md` - Shared module, Material module, 9 components, pipes, directives, services
- `angular-styles-foundation.md` - Design system (.editorconfig, styles.scss, 19 SCSS partials)
- `angular-app-foundation.md` - App root files (app.component, app.config, app.routes)

## 6. Proxy Configuration

Create `src/ui/proxy.conf.json`:

```json
{
  "/api": {
    "target": "http://localhost:<API_PORT>",
    "secure": false,
    "changeOrigin": false,
    "logLevel": "debug",
    "ws": true
  }
}
```

Replace `<API_PORT>` with the configured API port.

## 7. Update angular.json

Add proxy configuration to serve options in `angular.json`:

```json
{
  "serve": {
    "options": {
      "proxyConfig": "proxy.conf.json"
    }
  }
}
```
