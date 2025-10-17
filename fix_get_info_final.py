#!/usr/bin/env python3
"""
Fix all get_info() methods in tools to return proper JSON schema format
"""

import os
import re

def fix_tool_file(filepath):
    """Fix a single tool file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract API name from filename
    api_name = os.path.basename(filepath)[:-3]  # Remove .py
    
    # Determine if it's a GET or SET tool
    is_setter = any(prefix in api_name for prefix in [
        'manage_', 'create_', 'record_', 'send_', 'use_', 
        'move_', 'clone_', 'decide_'
    ])
    
    tool_type = "Setter" if is_setter else "Getter"
    
    # Create the correct get_info method
    new_get_info = f'''    @staticmethod
    def get_info() -> dict[str, Any]:
        return {{
            "tool_name": "{api_name}",
            "category": "Management", 
            "description": "Manages {api_name.replace('_', ' ')} records.",
            "arguments": "payload: Dict[str, Any]",
            "flag": "{tool_type}"
        }}'''
    
    # Remove any existing get_info method
    pattern = r'@staticmethod\s+def get_info\(\) -> dict\[str, Any\]:.*?return \{.*?\}'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Clean up any extra braces or syntax issues
    content = re.sub(r'\s*}\s*}\s*$', '}', content)
    content = re.sub(r'\s*}\s*,\s*$', '}', content)
    
    # Add the new get_info method before the final closing brace
    lines = content.split('\n')
    # Find the last closing brace of the class
    last_brace_index = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '}':
            last_brace_index = i
            break
    
    if last_brace_index > 0:
        lines.insert(last_brace_index, new_get_info)
        content = '\n'.join(lines)
    
    # Write the fixed content
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    tools_dir = '/Users/fenetshewarega/Desktop/bruk-new/wiki_confluence/tools/interface_1'
    
    # Get all tool files
    tool_files = [f for f in os.listdir(tools_dir) 
                  if f.endswith('.py') and f not in ['base.py', 'data_manager.py', '__init__.py']]
    
    print(f'🔧 Fixing {len(tool_files)} tool files...')
    
    for filename in tool_files:
        filepath = os.path.join(tools_dir, filename)
        print(f'  Processing {filename}...')
        try:
            fix_tool_file(filepath)
        except Exception as e:
            print(f'    ❌ Error fixing {filename}: {e}')
    
    print('✅ All tools fixed!')

if __name__ == '__main__':
    main()
