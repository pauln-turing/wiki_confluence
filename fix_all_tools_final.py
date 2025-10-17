#!/usr/bin/env python3
"""
Final fix for all tools - correct indentation and imports
"""

import os
from pathlib import Path

def fix_tool_file(file_path):
    """Fix a single tool file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix imports
    content = content.replace('from base import Tool', 'from .base import Tool')
    content = content.replace('from data_manager import DataManager', 'from .data_manager import DataManager')
    
    # Fix indentation issues in invoke method
    lines = content.split('\n')
    fixed_lines = []
    in_try_block = False
    try_indent = 0
    
    for i, line in enumerate(lines):
        # Detect try block start
        if 'try:' in line and 'data_manager = DataManager()' in lines[i+1] if i+1 < len(lines) else False:
            in_try_block = True
            try_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Fix indentation inside try block
        if in_try_block:
            if line.strip().startswith('if action ==') or line.strip().startswith('elif action ==') or line.strip().startswith('else:'):
                # This should be indented under try
                fixed_lines.append(' ' * (try_indent + 4) + line.strip())
                continue
            elif line.strip() == '':
                fixed_lines.append(line)
                continue
            elif line.strip().startswith('except Exception as e:'):
                in_try_block = False
                fixed_lines.append(line)
                continue
            elif line.strip().startswith('return json.dumps'):
                # This should be indented under the action blocks
                fixed_lines.append(' ' * (try_indent + 8) + line.strip())
                continue
            elif line.strip().startswith('#'):
                # Comments should be indented under action blocks
                fixed_lines.append(' ' * (try_indent + 8) + line.strip())
                continue
            elif line.strip().startswith('record_id =') or line.strip().startswith('record_data =') or line.strip().startswith('update_data =') or line.strip().startswith('data_manager.'):
                # These should be indented under action blocks
                fixed_lines.append(' ' * (try_indent + 8) + line.strip())
                continue
            else:
                fixed_lines.append(line)
                continue
        
        fixed_lines.append(line)
    
    # Write back the fixed content
    with open(file_path, 'w') as f:
        f.write('\n'.join(fixed_lines))

def main():
    """Fix all tools in the wiki/interface_1 directory"""
    tools_dir = Path("/Users/fenetshewarega/Desktop/bruk-new/wiki_confluence/wiki/interface_1")
    
    print("🔧 FIXING ALL TOOLS")
    print("=" * 50)
    
    fixed_count = 0
    for file_path in tools_dir.glob("*.py"):
        if file_path.name in ["base.py", "data_manager.py", "__init__.py"]:
            continue
            
        print(f"Fixing {file_path.name}...")
        try:
            fix_tool_file(file_path)
            fixed_count += 1
            print(f"✅ {file_path.name} fixed")
        except Exception as e:
            print(f"❌ Error fixing {file_path.name}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count} tools!")

if __name__ == "__main__":
    main()
