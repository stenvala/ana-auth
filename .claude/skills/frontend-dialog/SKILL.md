---
name: frontend-dialog
description: Create Angular Material dialog components with static open pattern
---

# Frontend Dialog Creation

Create Angular Material dialog components following the static open pattern with typed interfaces.

## When to Use

- Creating modal dialogs for forms (create/edit)
- Complex interactions that need to return data
- Multi-step wizards in a modal
- Confirmation dialogs with custom content

## Prerequisites

1. Feature module/structure exists
2. Required services available for business logic

## Naming Convention

- **Component class**: `<Feature>Dialog<Name>Component`
- **Selector**: `<feature>-dialog-<name>`
- **Input interface**: `<Feature>Dialog<Name>InputData`
- **Output interface**: `<Feature>Dialog<Name>OutputData`
- **Folder**: `<feature>-dialog-<name>/` inside the feature's components directory

## Scaffolding Script

```bash
uv run .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py <feature> <dialog-name>
```

Example:
```bash
uv run .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py accounting edit-bank-account
```

This generates the component `.ts` and `.html` files in the feature's components directory.

## Instructions

1. **Scaffold**: Run the init script above
2. **Complete the component**: Fill in generated TODOs (interfaces, form fields, validators, save logic)
3. **Export**: Add export to the feature's `components/index.ts`
4. **Verify build**:
   ```bash
   source ~/.nvm/nvm.sh && nvm use 20.19.2 && cd src/ui && npx ng build --configuration=development 2>&1 | head -20
   ```

## Key Rules

### Interface Definitions
1. **Always define both**: `InputData` and `OutputData`, even if one is empty
2. **undefined return**: Dialog returns `undefined` when cancelled

### Static Open Method
3. **Signature**: `static async open(dialog: MatDialog, data: InputData): Promise<OutputData | undefined>`
4. **Use firstValueFrom**: Convert `afterClosed()` observable to promise

### Component Structure
5. **OnPush change detection**: Always `ChangeDetectionStrategy.OnPush`
6. **Inject dependencies**: Use `inject()` for `MatDialogRef`, `MAT_DIALOG_DATA`, and services
7. **Protected data**: Mark injected data as `protected` for template access

### Close Behavior
8. **Cancel**: `dialogRef.close()` without arguments (returns undefined)
9. **Submit**: `dialogRef.close(outputData)` with typed result after validation

### Module Imports
10. **Use shared modules**: Import `[CoreModule, MaterialModule, SharedModule, FormField]` for form dialogs — never import Mat\* individually
11. **Dialog DI imports**: Import `MAT_DIALOG_DATA`, `MatDialogRef`, `MatDialog` as TypeScript value imports

### Form Dialogs
**IMPORTANT**: For dialogs with forms, use the `/frontend-forms` skill for signal-based form patterns.

## Resources

| Resource | Contents |
|----------|----------|
| `resources/dialog-template.md` | Dialog component pattern with forms |

