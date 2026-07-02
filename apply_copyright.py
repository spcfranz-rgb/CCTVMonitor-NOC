#!/usr/bin/env python3
import os
from pathlib import Path

# The base copyright text
YEAR = "2026"
OWNER = "Timothy Franz"
COPYRIGHT_TEXT = f"""Copyright (c) {YEAR} {OWNER}. All Rights Reserved.

This file is part of Project Lighthouse.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential."""

# Formatters based on file type
HEADERS = {
    "hash": "\n".join([f"# {line}" if line else "#" for line in COPYRIGHT_TEXT.split('\n')]) + "\n\n",
    "js": "/*\n" + "\n".join([f" * {line}" if line else " *" for line in COPYRIGHT_TEXT.split('\n')]) + "\n */\n\n",
    "html": "<!--\n" + COPYRIGHT_TEXT + "\n-->\n\n"
}

# Map extensions to their comment style
EXTENSION_MAP = {
    '.py': 'hash',
    '.yml': 'hash',
    '.yaml': 'hash',
    '.sh': 'hash',
    '.js': 'js',
    '.vue': 'html',
    '.html': 'html'
}

def inject_header(file_path):
    path = Path(file_path)
    
    # Handle extensionless files like Dockerfile
    ext = path.suffix
    if path.name == 'Dockerfile':
        style = 'hash'
    else:
        style = EXTENSION_MAP.get(ext)
        
    if not style:
        return # Skip unsupported file types

    header_content = HEADERS[style]

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            return

        # Prevent double-injection
        content_str = "".join(lines)
        if "Copyright (c)" in content_str and OWNER in content_str:
            print(f"Skipping (Already Stamped): {path.name}")
            return

        insert_idx = 0
        
        # Safely bypass shebangs so they remain at the absolute top
        if lines[0].startswith("#!"):
            insert_idx = 1
            
        lines.insert(insert_idx, header_content)

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        print(f"Stamped: {path.relative_to(Path.cwd())}")

    except Exception as e:
        print(f"Failed to process {path.name}: {e}")

def main():
    target_dirs = ['.', 'frontend', 'mosquitto']
    ignore_dirs = ['node_modules', '.git', '__pycache__', 'dist']

    for d in target_dirs:
        base_path = Path(d)
        if not base_path.exists():
            continue
            
        for path in base_path.rglob('*'):
            if path.is_file():
                # Skip ignored directories
                if any(ignored in path.parts for ignored in ignore_dirs):
                    continue
                inject_header(path)

if __name__ == "__main__":
    print("Starting Project Lighthouse Copyright Injection...")
    main()
    print("Done.")
