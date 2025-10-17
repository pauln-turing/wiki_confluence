import pandas as pd
import os

# read the CSV file
df = pd.read_csv("tools.csv")

# Create the tools directory
if not os.path.exists('tool'):
    os.makedirs('tool')


# Function to convert snake_case to PascalCase
def to_pascal_case(snake_case_string):
    return ''.join(word.capitalize() for word in snake_case_string.split('_'))

# Generate Python files for each tool
for index, row in df.iterrows():
    tool_name = row['tool_name']
    class_name = to_pascal_case(tool_name)
    file_name = f'tool/{tool_name}.py'
    
    # Escape quotes in arguments and description for the Python string
    arguments_str = row['arguments'].replace("'", "\\'").replace('"', '\\"')
    description_str = row['description'].replace("'", "\\'").replace('"', '\\"')
    
    # Generate the class code
    tool_code = f"""
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class {class_name}(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        # TODO: Implement tool invocation logic here.
        # This is a placeholder and should be replaced with the actual implementation.
        raise NotImplementedError("This tool has not been implemented yet.")

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {{
            "tool_name": "{tool_name}",
            "category": "{row['category']}",
            "description": "{description_str}",
            "arguments": "{arguments_str}",
            "flag": "{row['flag']}"
        }}

"""
    
    # Write the code to the file
    with open(file_name, 'w') as f:
        f.write(tool_code)

print("Python tool classes have been successfully generated in the 'tools' directory.")