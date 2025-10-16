import json
import os
import re
import sys

def parse_schema(schema_content: str) -> tuple[dict, list]:
    """
    Parses the schema content to extract table primary keys and foreign key relationships.
    """
    tables = {}
    relationships = []

    # Regex patterns to find definitions
    table_pattern = re.compile(r"Table\s+(\w+)\s*\{")
    pk_pattern = re.compile(r"^\s*(\w+)\s+.*\s+\[primary key\]")
    ref_pattern = re.compile(r"Ref\s*.*:\s*(\w+)\.(\w+)\s*>\s*(\w+)\.(\w+)")

    current_table = None
    for line in schema_content.splitlines():
        table_match = table_pattern.match(line)
        if table_match:
            current_table = table_match.group(1)
            tables[current_table] = {'pk_column': None}
            continue

        if current_table:
            pk_match = pk_pattern.match(line)
            if pk_match and not tables[current_table]['pk_column']:
                tables[current_table]['pk_column'] = pk_match.group(1)
        
        ref_match = ref_pattern.match(line)
        if ref_match:
            from_table, from_column, to_table, _ = ref_match.groups()
            relationships.append({
                'from_table': from_table,
                'from_column': from_column,
                'to_table': to_table
            })
            
    return tables, relationships

def load_json_data(directory: str) -> dict:
    """
    Loads all .json files from a directory into a dictionary keyed by table name.
    """
    all_data = {}
    print(f"📂 Loading JSON seed files from './{directory}' folder...")
    if not os.path.isdir(directory):
        print(f"  -> ⚠️  Error: Directory '{directory}' not found.", file=sys.stderr)
        return None

    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".json"):
            table_name = filename[:-5]
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_data[table_name] = json.load(f)
                    print(f"  -> Loaded '{filename}' ({len(all_data[table_name])} records)")
            except (json.JSONDecodeError, IOError) as e:
                print(f"  -> ⚠️  Could not load or parse {filename}. Error: {e}", file=sys.stderr)
    return all_data

def verify_integrity(tables: dict, relationships: list, all_data: dict) -> list:
    """
    Checks for orphan foreign keys based on the parsed schema and loaded data.
    """
    errors = []
    
    # Pre-calculate all primary keys from the JSON data for fast lookups
    # The primary keys are the top-level keys in each JSON file.
    primary_keys = {table: set(table_data.keys()) for table, table_data in all_data.items()}

    for rel in relationships:
        from_table = rel['from_table']
        from_column = rel['from_column']
        to_table = rel['to_table']

        if from_table not in all_data or to_table not in all_data:
            print(f"  -> ⚠️  Skipping check for '{from_table}' -> '{to_table}': One or both JSON files are missing.", file=sys.stderr)
            continue

        parent_pks = primary_keys.get(to_table, set())
        child_records = all_data.get(from_table, {}).values()
        pk_column = tables.get(from_table, {}).get('pk_column', 'Unknown_PK')

        for record in child_records:
            record_id = record.get(pk_column, 'Unknown ID')
            fk_value = record.get(from_column)

            # Check for orphans: FK is not null and doesn't exist in the parent's primary keys
            if fk_value is not None and str(fk_value) not in parent_pks:
                error_msg = (
                    f"Table '{from_table}', Record with {pk_column}='{record_id}': "
                    f"Foreign key '{from_column}' has orphan value '{fk_value}'. "
                    f"This ID was not found in table '{to_table}'."
                )
                errors.append(error_msg)
                
    return errors

def main():
    """
    Main function to orchestrate the verification process.
    """
    schema_file_name = 'schema.dbml' # The name of your schema file
    data_directory = 'generated_data' # The folder containing the JSON files
    
    try:
        with open(data_directory + "/" + schema_file_name, 'r', encoding='utf-8') as f:
            schema_content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Schema file '{schema_file_name}' not found in the current directory.", file=sys.stderr)
        return

    print("🔍 Parsing schema...")
    tables, relationships = parse_schema(schema_content)
    print(f"  -> Found {len(tables)} tables and {len(relationships)} relationships.")
    
    all_data = load_json_data(data_directory)
    if not all_data:
        print(f"❌ Error: No JSON data files were loaded from the './{data_directory}' directory.", file=sys.stderr)
        return
        
    print("\n🔗 Verifying referential integrity...")
    errors = verify_integrity(tables, relationships, all_data)
    
    print("\n" + "="*50)
    if not errors:
        print("✅ All checks passed! The database seed is consistent.")
    else:
        print(f"❌ Found {len(errors)} inconsistencies (orphan records):")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")
    print("="*50)

if __name__ == "__main__":
    main()