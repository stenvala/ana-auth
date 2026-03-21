#!/usr/bin/env python3
"""
Initialize an Angular dialog component by loading the scaffold template
from dialog-template.md and replacing tokens with actual names.

Usage:
    python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py <feature> <dialog-name>

Example:
    python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py accounting edit-bank-account

This creates:
    src/ui/src/app/features/accounting/components/accounting-dialog-edit-bank-account/
        accounting-dialog-edit-bank-account.component.ts
        accounting-dialog-edit-bank-account.component.html
"""

import re
import sys
from pathlib import Path


TEMPLATE_FILE = Path(__file__).parent.parent / "resources" / "dialog-template.md"


def to_pascal_case(kebab_name: str) -> str:
    """Convert kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in kebab_name.split("-"))


def to_camel_case(kebab_name: str) -> str:
    """Convert kebab-case to camelCase."""
    parts = kebab_name.split("-")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def extract_scaffold(template_content: str, marker: str) -> str:
    """Extract code block content following a scaffold marker comment."""
    # Find the marker comment (e.g., <!-- scaffold:ts -->)
    pattern = rf"<!-- scaffold:{marker} -->\s*```\w+\n(.*?)```"
    match = re.search(pattern, template_content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find scaffold marker '<!-- scaffold:{marker} -->' in template")
    return match.group(1)


def replace_tokens(content: str, feature_pascal: str, feature_kebab: str,
                   name_pascal: str, name_kebab: str, form_name: str) -> str:
    """Replace scaffold tokens with actual values."""
    content = content.replace("__FEATURE__", feature_pascal)
    content = content.replace("__feature__", feature_kebab)
    content = content.replace("__NAME__", name_pascal)
    content = content.replace("__name__", name_kebab)
    content = content.replace("__FORM__", form_name)
    return content


def create_dialog_component(feature: str, dialog_name: str):
    """Create a dialog component from the scaffold template."""

    # Read template
    if not TEMPLATE_FILE.exists():
        print(f"Error: Template file not found: {TEMPLATE_FILE}")
        sys.exit(1)

    template_content = TEMPLATE_FILE.read_text()

    # Compute names
    feature_pascal = to_pascal_case(feature)
    name_pascal = to_pascal_case(dialog_name)
    form_name = to_camel_case(dialog_name)
    folder_name = f"{feature}-dialog-{dialog_name}"
    component_name = f"{feature_pascal}Dialog{name_pascal}Component"
    selector = f"{feature}-dialog-{dialog_name}"

    # Extract scaffold templates
    ts_content = extract_scaffold(template_content, "ts")
    html_content = extract_scaffold(template_content, "html")

    # Replace tokens
    ts_content = replace_tokens(ts_content, feature_pascal, feature, name_pascal, dialog_name, form_name)
    html_content = replace_tokens(html_content, feature_pascal, feature, name_pascal, dialog_name, form_name)

    # Paths
    base_path = Path("src/ui/src/app/features") / feature / "components" / folder_name
    ts_file = base_path / f"{folder_name}.component.ts"
    html_file = base_path / f"{folder_name}.component.html"

    # Create directory
    base_path.mkdir(parents=True, exist_ok=True)

    # Write files
    ts_file.write_text(ts_content)
    html_file.write_text(html_content)

    print(f"Created dialog component:")
    print(f"  {ts_file}")
    print(f"  {html_file}")
    print()
    print(f"Component: {component_name}")
    print(f"Selector: {selector}")
    print()
    print("TODO:")
    print("  1. Define InputData and OutputData interfaces")
    print("  2. Define FormModel interface and form fields")
    print("  3. Add validators to form()")
    print("  4. Inject your feature service and SharedNotificationService")
    print("  5. Implement save logic in onSubmit (Pattern B)")
    print("  6. Add form fields to HTML template")
    print("  7. Export from feature's components/index.ts")
    print()
    print(f"Template loaded from: {TEMPLATE_FILE}")
    print("See dialog-template.md Pattern B for the complete reference pattern.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py <feature> <dialog-name>")
        print("Example: python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py accounting edit-bank-account")
        sys.exit(1)

    feature = sys.argv[1]
    dialog_name = sys.argv[2]

    create_dialog_component(feature, dialog_name)
