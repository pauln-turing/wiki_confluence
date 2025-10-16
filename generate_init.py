#!/usr/bin/env python3
import os
import sys

def snake_to_pascal(name: str) -> str:
    """Converts snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split('_'))

def generate_init_file(directory_path: str):
    """
    Traverses a directory to find Python files, extracts class names,
    and generates an __init__.py file with the correct imports and list.
    """
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at '{directory_path}'")
        sys.exit(1)

    tools_list = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]  # Remove '.py'
            class_name = snake_to_pascal(module_name)
            tools_list.append((module_name, class_name))

    tools_list.sort(key=lambda x: x[0])  # Sort by module name for a clean, consistent output

    imports = []
    class_names = []

    for module_name, class_name in tools_list:
        imports.append(f"from .{module_name} import {class_name}")
        class_names.append(class_name)
    
    # Check if we are in an interface folder to name the list correctly
    parent_dir_name = os.path.basename(directory_path)
    if parent_dir_name.startswith("interface_"):
        interface_number = parent_dir_name.split("_")[1]
        list_name = f"ALL_TOOLS_INTERFACE_{interface_number}"
    else:
        list_name = "ALL_TOOLS"

    init_content = "\n".join(imports)
    init_content += "\n\n"
    init_content += f"{list_name} = [\n"
    init_content += ",\n".join(f"    {class_name}" for class_name in class_names)
    init_content += "\n]\n"
    
    # Write to __init__.py in the specified directory
    init_file_path = os.path.join(directory_path, '__init__.py')
    try:
        with open(init_file_path, 'w') as f:
            f.write(init_content)
        print(f"Successfully generated '{init_file_path}' with {len(tools_list)} tools.")
    except Exception as e:
        print(f"Failed to write to '{init_file_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_init.py <directory_path>")
        sys.exit(1)
    
    target_directory = sys.argv[1]
    generate_init_file(target_directory)