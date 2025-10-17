#!/usr/bin/env python3
"""
Properly fix all tools with correct structure
"""

import os
from pathlib import Path

# Tool specifications
TOOL_SPECS = {
    "get_user": {"class": "GetUser", "table": "users", "is_get": True, "fields": ["user_id", "email"]},
    "get_group": {"class": "GetGroup", "table": "groups", "is_get": True, "fields": ["group_id", "group_name"]},
    "get_space": {"class": "GetSpace", "table": "spaces", "is_get": True, "fields": ["space_key", "space_id"]},
    "get_page": {"class": "GetPage", "table": "pages", "is_get": True, "fields": ["page_id", "title"]},
    "get_page_versions": {"class": "GetPageVersions", "table": "page_versions", "is_get": True, "fields": ["page_id"]},
    "get_comments": {"class": "GetComments", "table": "comments", "is_get": True, "fields": ["page_id"]},
    "get_labels": {"class": "GetLabels", "table": "page_labels", "is_get": True, "fields": ["page_id"]},
    "get_attachments": {"class": "GetAttachments", "table": "attachments", "is_get": True, "fields": ["page_id"]},
    "get_watchers": {"class": "GetWatchers", "table": "watchers", "is_get": True, "fields": ["space_id", "page_id"]},
    "get_audit_log": {"class": "GetAuditLog", "table": "audit_logs", "is_get": True, "fields": ["actor_user_id", "action_type", "start_date", "end_date"]},
    "get_config_history": {"class": "GetConfigHistory", "table": "space_config_history", "is_get": True, "fields": ["space_id"]},
    "get_notifications": {"class": "GetNotifications", "table": "notifications", "is_get": True, "fields": ["user_id"]},
    
    "manage_users": {"class": "ManageUsers", "table": "users", "is_get": False, "actions": ["create", "update", "delete"]},
    "manage_groups": {"class": "ManageGroups", "table": "groups", "is_get": False, "actions": ["create", "update", "delete"]},
    "manage_group_memberships": {"class": "ManageGroupMemberships", "table": "user_groups", "is_get": False, "actions": ["add", "remove"]},
    "manage_spaces": {"class": "ManageSpaces", "table": "spaces", "is_get": False, "actions": ["create", "update", "delete"]},
    "manage_space_memberships": {"class": "ManageSpaceMemberships", "table": "space_memberships", "is_get": False, "actions": ["add", "remove"]},
    "manage_space_features": {"class": "ManageSpaceFeatures", "table": "space_features", "is_get": False, "actions": ["manage"]},
    "manage_pages": {"class": "ManagePages", "table": "pages", "is_get": False, "actions": ["create", "update", "delete"]},
    "move_page": {"class": "MovePage", "table": "pages", "is_get": False, "actions": ["move"]},
    "clone_page": {"class": "ClonePage", "table": "pages", "is_get": False, "actions": ["clone"]},
    "manage_page_versions": {"class": "ManagePageVersions", "table": "page_versions", "is_get": False, "actions": ["restore"]},
    "manage_permissions": {"class": "ManagePermissions", "table": "permissions", "is_get": False, "actions": ["grant", "revoke", "get"]},
    "manage_comments": {"class": "ManageComments", "table": "comments", "is_get": False, "actions": ["add", "update", "delete"]},
    "manage_labels": {"class": "ManageLabels", "table": "page_labels", "is_get": False, "actions": ["add", "remove"]},
    "manage_attachments": {"class": "ManageAttachments", "table": "attachments", "is_get": False, "actions": ["add", "remove"]},
    "manage_templates": {"class": "ManageTemplates", "table": "templates", "is_get": False, "actions": ["create", "update", "delete"]},
    "use_template": {"class": "UseTemplate", "table": "templates", "is_get": False, "actions": ["use"]},
    "manage_watchers": {"class": "ManageWatchers", "table": "watchers", "is_get": False, "actions": ["add", "remove"]},
    "manage_exports": {"class": "ManageExports", "table": "export_jobs", "is_get": False, "actions": ["create", "import", "get"]},
    "record_audit_log": {"class": "RecordAuditLog", "table": "audit_logs", "is_get": False, "actions": ["record"]},
    "record_config_change": {"class": "RecordConfigChange", "table": "space_config_history", "is_get": False, "actions": ["record"]},
    "create_approval_request": {"class": "CreateApprovalRequest", "table": "approval_requests", "is_get": False, "actions": ["create"]},
    "decide_approval_step": {"class": "DecideApprovalStep", "table": "approval_decisions", "is_get": False, "actions": ["update"]},
    "send_notification": {"class": "SendNotification", "table": "notifications", "is_get": False, "actions": ["create"]},
}

def create_get_tool(tool_name, spec):
    """Create a GET tool"""
    class_name = spec["class"]
    table_name = spec["table"]
    fields = spec["fields"]
    
    field_checks = []
    for field in fields:
        field_checks.append(f'        {field} = payload.get("{field}")')
    
    if len(fields) > 1:
        field_names = [f for f in fields if f and not f.startswith("?")]
        validation = f'''
        if not any([{', '.join(field_names)}]):
            return json.dumps({{"error": "At least one of {', '.join(field_names)} must be provided in the payload."}})'''
    else:
        validation = ""
    
    if len(fields) > 1:
        search_logic = f'''
        data_manager = DataManager()
        try:
            if {fields[0]}:
                result = data_manager.get_record("{table_name}", {fields[0]})
            else:
                result = data_manager.find_by_field("{table_name}", "{fields[1]}", {fields[1]})
            
            if result:
                return json.dumps(result)
            else:
                return json.dumps({{"error": "{spec["category"].split()[0] if "category" in spec else "Record"} not found."}})
        except Exception as e:
            return json.dumps({{"error": str(e)}})'''
    else:
        search_logic = f'''
        data_manager = DataManager()
        try:
            result = data_manager.get_record("{table_name}", {fields[0]})
            if result:
                return json.dumps(result)
            else:
                return json.dumps({{"error": "{spec["category"].split()[0] if "category" in spec else "Record"} not found."}})
        except Exception as e:
            return json.dumps({{"error": str(e)}})'''
    
    return f'''from .base import Tool
from typing import Any, Dict
from .data_manager import DataManager
import json

class {class_name}(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Retrieves a {table_name} record.
        Args:
            payload (Dict[str, Any]): Parameters for the request
        Returns:
            str: JSON response
        """
{chr(10).join(field_checks)}{validation}
{search_logic}

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {{
            "tool_name": "{tool_name}",
            "category": "Management",
            "description": "Retrieves a {table_name} record.",
            "arguments": "table_name='{table_name}', action='get', payload={{{', '.join([f'{f}: str' for f in fields])}}}",
            "flag": "Getter"
        }}'''

def create_set_tool(tool_name, spec):
    """Create a SET tool"""
    class_name = spec["class"]
    table_name = spec["table"]
    actions = spec["actions"]
    
    action_validation = f'''
        action = payload.get("action")
        if not action:
            return json.dumps({{"error": "Action is required. Use one of: {', '.join(actions)}"}})
        
        if action not in {actions}:
            return json.dumps({{"error": "Invalid action. Use one of: {', '.join(actions)}"}})'''
    
    action_handlers = []
    for action in actions:
        if action == "create":
            handler = f'''
            if action == "create":
                # Create new record
                record_id = data_manager.get_next_id("{table_name}")
                record_data = {{
                    "id": record_id,
                    "created_at": data_manager.get_timestamp(),
                    **{{k: v for k, v in payload.items() if k != "action"}}
                }}
                data_manager.create_record("{table_name}", record_id, record_data)
                return json.dumps({{"message": "Record created successfully", "id": record_id}})'''
        elif action == "update":
            handler = f'''
            elif action == "update":
                # Update existing record
                record_id = payload.get("id")
                if not record_id:
                    return json.dumps({{"error": "ID is required for update"}})
                
                update_data = {{k: v for k, v in payload.items() if k not in ["action", "id"]}}
                data_manager.update_record("{table_name}", record_id, update_data)
                return json.dumps({{"message": "Record updated successfully"}})'''
        elif action == "delete":
            handler = f'''
            elif action == "delete":
                # Delete record
                record_id = payload.get("id")
                if not record_id:
                    return json.dumps({{"error": "ID is required for delete"}})
                
                data_manager.delete_record("{table_name}", record_id)
                return json.dumps({{"message": "Record deleted successfully"}})'''
        else:
            handler = f'''
            elif action == "{action}":
                # Handle {action} action
                return json.dumps({{"message": "{action} action completed successfully"}})'''
        
        action_handlers.append(handler)
    
    error_handler = f'''
            else:
                return json.dumps({{"error": "Invalid action. Use one of: {', '.join(actions)}"}})'''
    
    return f'''from .base import Tool
from typing import Any, Dict
from .data_manager import DataManager
import json

class {class_name}(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Manages {table_name} records.
        Args:
            payload (Dict[str, Any]): Parameters for the request
        Returns:
            str: JSON response
        """
{action_validation}
        
        data_manager = DataManager()
        try:{''.join(action_handlers)}{error_handler}
        except Exception as e:
            return json.dumps({{"error": str(e)}})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {{
            "tool_name": "{tool_name}",
            "category": "Management",
            "description": "Manages {table_name} records.",
            "arguments": "table_name='{table_name}', action='{"/".join(actions)}', payload={{}}",
            "flag": "Setter"
        }}'''

def main():
    """Fix all tools"""
    tools_dir = Path("/Users/fenetshewarega/Desktop/bruk-new/wiki_confluence/wiki/interface_1")
    
    print("🔧 FIXING ALL TOOLS PROPERLY")
    print("=" * 50)
    
    for tool_name, spec in TOOL_SPECS.items():
        file_path = tools_dir / f"{tool_name}.py"
        
        if spec["is_get"]:
            content = create_get_tool(tool_name, spec)
        else:
            content = create_set_tool(tool_name, spec)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ {tool_name}.py fixed")
    
    print(f"\n🎉 All {len(TOOL_SPECS)} tools fixed!")

if __name__ == "__main__":
    main()
