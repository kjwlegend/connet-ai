#!/usr/bin/env python3
"""
Fix SQLAlchemy dict type errors

This script automatically adds sa_column=Column(JSON) to all dict fields
in SQLModel database models that don't already have it.

This fixes the error: ValueError: <class 'dict'> has no matching SQLAlchemy type
"""

import os
import re
from pathlib import Path


def fix_dict_fields_in_file(file_path: Path):
    """Fix dict fields without SQLAlchemy column types in a single model file."""
    print(f"Processing: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Check if Column and JSON are already imported
        has_column_import = "from sqlalchemy import" in content and "Column" in content
        has_json_import = "from sqlalchemy import" in content and "JSON" in content

        # Add imports if needed
        if not has_column_import or not has_json_import:
            # Find the sqlmodel import line
            sqlmodel_import_pattern = r"(from sqlmodel import [^\n]+)"

            def add_imports(match):
                imports_to_add = []
                if not has_column_import:
                    imports_to_add.append("Column")
                if not has_json_import:
                    imports_to_add.append("JSON")

                if imports_to_add:
                    import_line = match.group(1)
                    new_import = f"{import_line}\nfrom sqlalchemy import {', '.join(imports_to_add)}"
                    return new_import
                return match.group(1)

            content = re.sub(sqlmodel_import_pattern, add_imports, content)

        # Pattern to match dict fields without sa_column
        # Matches: field_name: dict = Field(...) or field_name: Optional[dict] = Field(...)
        # But excludes those that already have sa_column=Column(JSON)
        dict_field_pattern = (
            r"(\s+)(\w+):\s+(?:Optional\[)?dict\]?\s*=\s*Field\(\s*([^)]*)\)"
        )

        def fix_dict_field(match):
            indent = match.group(1)
            field_name = match.group(2)
            field_args = match.group(3)

            # Skip if sa_column is already present
            if "sa_column" in field_args:
                return match.group(0)

            # Add sa_column=Column(JSON) to the field arguments
            if field_args.strip():
                # There are existing arguments
                if field_args.strip().endswith(","):
                    new_args = f"{field_args}\n{indent}    sa_column=Column(JSON),"
                else:
                    new_args = f"{field_args},\n{indent}    sa_column=Column(JSON)"
            else:
                # No existing arguments
                new_args = f"\n{indent}    sa_column=Column(JSON)"

            # Reconstruct the field
            field_type = (
                "dict" if "Optional[dict]" not in match.group(0) else "Optional[dict]"
            )
            return f"{indent}{field_name}: {field_type} = Field({new_args}\n{indent})"

        # Apply the replacement
        content = re.sub(dict_field_pattern, fix_dict_field, content, flags=re.DOTALL)

        # If we made changes, write the file back
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to process all model files."""
    # Get the models directory
    models_dir = (
        Path(__file__).parent.parent / "app" / "infrastructure" / "database" / "models"
    )

    if not models_dir.exists():
        print(f"Models directory not found: {models_dir}")
        return

    print(f"Scanning models directory: {models_dir}")

    # Find all Python model files
    model_files = list(models_dir.glob("*.py"))
    model_files = [f for f in model_files if f.name != "__init__.py"]

    print(f"Found {len(model_files)} model files")

    updated_count = 0
    for model_file in model_files:
        if fix_dict_fields_in_file(model_file):
            updated_count += 1

    print(f"\nSummary: Updated {updated_count} out of {len(model_files)} files")

    if updated_count > 0:
        print("\nAll model files have been updated with proper JSON column types!")
        print("The SQLAlchemy dict type errors should now be resolved.")
    else:
        print("\nAll model files already have proper JSON column types.")


if __name__ == "__main__":
    main()
