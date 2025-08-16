#!/usr/bin/env python3
"""
Fix BaseRepository generic type issues in all repository files.
"""

import os
import re
from pathlib import Path

def fix_repository_file(file_path: Path):
    """Fix BaseRepository generic types in a single file."""
    print(f"Processing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match BaseRepository[ModelType] and add UUID as second type parameter
    # This assumes all models use UUID as their ID type
    pattern = r'BaseRepository\[([A-Za-z_][A-Za-z0-9_]*)\]'
    replacement = r'BaseRepository[\1, UUID]'
    
    content = re.sub(pattern, replacement, content)
    
    # Make sure UUID is imported if we made changes
    if content != original_content:
        # Check if UUID is already imported
        if 'from uuid import UUID' not in content and 'import UUID' not in content:
            # Add UUID import after existing uuid imports if they exist
            if 'from uuid import' in content:
                content = re.sub(
                    r'(from uuid import [^,\n]+)',
                    r'\1, UUID',
                    content
                )
            elif 'import uuid' in content:
                # Add UUID import after other imports
                import_section = content.split('\n\n')[0]  # Get first paragraph (imports)
                rest = content[len(import_section):]
                if 'from uuid import UUID' not in import_section:
                    import_section += '\nfrom uuid import UUID'
                content = import_section + rest
            else:
                # Add UUID import near the top after typing imports
                lines = content.split('\n')
                insert_index = 0
                for i, line in enumerate(lines):
                    if line.startswith('from typing import') or line.startswith('import typing'):
                        insert_index = i + 1
                        break
                    elif line.startswith('from') or line.startswith('import'):
                        insert_index = i + 1
                
                lines.insert(insert_index, 'from uuid import UUID')
                content = '\n'.join(lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed {file_path.name}")
    else:
        print(f"No changes needed for {file_path.name}")

def main():
    """Fix all repository files."""
    repo_dir = Path("app/infrastructure/database/repositories")
    
    if not repo_dir.exists():
        print(f"Directory {repo_dir} not found!")
        return
    
    for py_file in repo_dir.glob("*_repository_impl.py"):
        fix_repository_file(py_file)

if __name__ == "__main__":
    main()