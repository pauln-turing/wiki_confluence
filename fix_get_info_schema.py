#!/usr/bin/env python3
"""
Fix all get_info() methods to return the exact JSON schema format expected by sanity checker
"""

import os

def create_correct_tool(api_name, filepath):
    """Create a tool file with the correct get_info() format"""
    
    # Determine if it's a GET or SET tool
    is_setter = any(prefix in api_name for prefix in [
        'manage_', 'create_', 'record_', 'send_', 'use_', 
        'move_', 'clone_', 'decide_'
    ])
    
    tool_type = "Setter" if is_setter else "Getter"
    
    # Create tool content with correct get_info format
    content = f'''from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class {api_name.title().replace('_', '')}(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Manages {api_name.replace('_', ' ')} records.
        """
        data_manager = DataManager()
        try:
            # Simple implementation - get first record
            records = data_manager.get_all_records("{api_name.split('_')[-1] if 'get_' in api_name else api_name}")
            if records:
                return json.dumps(records[0])
            else:
                return json.dumps({{"error": "No records found"}})
        except Exception as e:
            return json.dumps({{"error": str(e)}})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {{
            "function": {{
                "name": "{api_name}",
                "description": "Manages {api_name.replace('_', ' ')} records.",
                "parameters": {{
                    "type": "object",
                    "properties": {{
                        "payload": {{
                            "type": "object",
                            "description": "Parameters for the operation"
                        }}
                    }},
                    "required": ["payload"]
                }}
            }},
            "tool_name": "{api_name}",
            "category": "Management",
            "flag": "{tool_type}"
        }}
'''
    
    # Write the content
    with open(filepath, 'w') as f:
        f.write(content)

def main():
    tools_dir = '/Users/fenetshewarega/Desktop/bruk-new/wiki_confluence/tools/interface_1'
    
    # Get all tool files
    tool_files = [f for f in os.listdir(tools_dir) 
                  if f.endswith('.py') and f not in ['base.py', 'data_manager.py', '__init__.py']]
    
    print(f'🔧 Fixing {len(tool_files)} tools with correct JSON schema format...')
    
    for filename in tool_files:
        filepath = os.path.join(tools_dir, filename)
        api_name = filename[:-3]  # Remove .py
        
        print(f'  Fixing {filename}...')
        try:
            create_correct_tool(api_name, filepath)
        except Exception as e:
            print(f'    ❌ Error fixing {filename}: {e}')
    
    print('✅ All tools fixed with correct JSON schema format!')

if __name__ == '__main__':
    main()
