# Angular Styles Foundation

## .editorconfig

Copy `references/templates/.editorconfig` to `src/ui/.editorconfig`.

## styles.scss

Copy `references/templates/styles/styles.scss` to `src/ui/src/styles.scss`.

This is the main design system entry point with a custom Material theme. Customize the primary/accent color palettes for each project.

## Style Partials

Copy all `_*.scss` files from `references/templates/styles/` to `src/ui/src/styles/`.

### Files Included

- `_variables.scss` - CSS custom properties (colors, gradients, shadows, spacing, typography, transitions)
- `_base.scss` - Global HTML/body styles, basic utilities
- `_layout.scss` - Flex utilities, spacing, page-centered, content-wrapper
- `_pages.scss` - Page containers (narrow, wide, fullscreen, scrollable), page headers, panels, info grids, edit forms
- `_components.scss` - Tables, badges, dialogs, drop zones, file displays, result/error boxes, linked items, dense/editable tables
- `_cards.scss` - Form cards, feature cards, card icons, cards grid, compact cards, panels
- `_grids.scss` - Card grid layouts for dashboards/settings
- `_forms.scss` - Form layout, full-width fields, actions, hints, sections
- `_dialogs.scss` - Dialog form layout, hints, section headers
- `_buttons.scss` - Submit buttons, loading/spinning/confirming states for loading-button directive
- `_alerts.scss` - Alert styles (error, success, warning)
- `_toolbar.scss` - App toolbar with gradient background, navigation links
- `_sections.scss` - Welcome sections, panels, day separators
- `_chips.scss` - Chip/tag styles with color variants
- `_resize.scss` - Resize handles for resizable panels
- `_drag-drop.scss` - CDK drag-drop patterns, animations, edit forms within items
- `_lists.scss` - Selectable list items for dialogs/pickers
- `_material-overrides.scss` - Angular Material component style overrides (cards, buttons, tables, menus, dialogs)
- `_badges.scss` - Comprehensive badge system with 20+ color variants and solid variants
