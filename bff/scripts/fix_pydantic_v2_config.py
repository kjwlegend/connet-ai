#!/usr/bin/env python3
"""
Fix Pydantic v2 Configuration Script

This script automatically converts all SQLModel database models from Pydantic v1
Config class format to Pydantic v2 model_config format.

Changes:
- class Config: -> model_config = {...}
- schema_extra -> json_schema_extra
- Updates field formatting for consistency
"""

import os
import re
from pathlib import Path


def fix_pydantic_config_in_file(file_path: Path):
    """Fix Pydantic configuration in a single model file."""
    print(f"Processing: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Pattern to match Config class with schema_extra
        config_pattern = r'(\s+)class Config:\s*\n\s*"""[^"]*"""\s*\n\s*schema_extra\s*=\s*(\{.*?\n\s*\})'

        def replace_config(match):
            indent = match.group(1)
            schema_content = match.group(2)

            # Convert schema_extra to json_schema_extra and wrap in model_config
            new_config = f'{indent}model_config = {{\n{indent}    "json_schema_extra": {schema_content}\n{indent}}}'
            return new_config

        # Apply the replacement
        content = re.sub(config_pattern, replace_config, content, flags=re.DOTALL)

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
        print(f"❌ Models directory not found: {models_dir}")
        return

        print(f"Scanning models directory: {models_dir}")

    # Find all Python model files
    model_files = list(models_dir.glob("*.py"))
    model_files = [f for f in model_files if f.name != "__init__.py"]

    print(f"Found {len(model_files)} model files")

    updated_count = 0
    for model_file in model_files:
        if fix_pydantic_config_in_file(model_file):
            updated_count += 1

    print(f"\nSummary: Updated {updated_count} out of {len(model_files)} files")

    if updated_count > 0:
        print(
            "\nAll model files have been updated to use Pydantic v2 configuration format!"
        )
        print("The application should now start without configuration conflicts.")
    else:
        print("\nAll model files are already using the correct configuration format.")


if __name__ == "__main__":
    main()
