#!/usr/bin/env python3
"""
Fix indentation errors in all tools
"""

import os
import re
from pathlib import Path

def fix_indentation_errors(file_path):
    """Fix indentation errors in a single tool file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for i, line in enumerate(lines):
        # Fix lines that have too much indentation (like line 16 in get_audit_log.py)
        if line.strip() and line.startswith('                ') and not line.startswith('        '):
            # This line has too much indentation, fix it
            fixed_line = '        ' + line.strip() + '\n'
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    # Write back the fixed content
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)

def main():
    """Fix all tools in the interface_1 directory"""
    tools_dir = Path("/Users/fenetshewarega/Desktop/bruk-new/wiki_confluence/tools/interface_1")
    
    print("🔧 FIXING INDENTATION ERRORS")
    print("=" * 50)
    
    fixed_count = 0
    for file_path in tools_dir.glob("*.py"):
        if file_path.name in ["base.py", "data_manager.py", "__init__.py"]:
            continue
            
        print(f"Fixing {file_path.name}...")
        try:
            fix_indentation_errors(file_path)
            fixed_count += 1
            print(f"✅ {file_path.name} fixed")
        except Exception as e:
            print(f"❌ Error fixing {file_path.name}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count} tools!")
    
    # Test compilation
    print("\n🧪 Testing compilation...")
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile'] + list(tools_dir.glob('*.py')), 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All tools compile successfully!")
    else:
        print("❌ Compilation errors found:")
        print(result.stderr)

if __name__ == "__main__":
    main()
