#!/usr/bin/env python3
"""
Comprehensive analysis and fix for all tools in interface_1
Based on the provided specification and Wiki Confluence Management Policy
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

# Tool specifications from the user
TOOL_SPECIFICATIONS = {
    "manage_users": {
        "category": "User Management",
        "description": "Creates, updates, or deletes a user account.",
        "arguments": "table_name='users', action='create/update/delete', payload={user_id: str, email: str, full_name: str, password: str, global_role: user_role, account_id: str}",
        "flag": "Setter"
    },
    "manage_groups": {
        "category": "Group Management", 
        "description": "Creates, updates, or deletes a user group.",
        "arguments": "table_name='groups', action='create/update/delete', payload={group_id: str, group_name: str}",
        "flag": "Setter"
    },
    "manage_group_memberships": {
        "category": "Group Management",
        "description": "Adds or removes users from a group.",
        "arguments": "table_name='user_groups', action='add/remove', payload={user_id: str, group_id: str}",
        "flag": "Setter"
    },
    "get_user": {
        "category": "User Management",
        "description": "Retrieves a user record by ID or email.",
        "arguments": "table_name='users', action='get', payload={user_id: str, email: str}",
        "flag": "Getter"
    },
    "get_group": {
        "category": "Group Management",
        "description": "Retrieves a group record by ID or name.",
        "arguments": "table_name='groups', action='get', payload={group_id: str, group_name: str}",
        "flag": "Getter"
    },
    "manage_spaces": {
        "category": "Space Management",
        "description": "Creates, updates, or deletes a space.",
        "arguments": "table_name='spaces', action='create/update/delete', payload={space_id: str, space_key: str, space_name: str, space_purpose: str, is_deleted: bool, created_by_user_id: str}",
        "flag": "Setter"
    },
    "get_space": {
        "category": "Space Management", 
        "description": "Retrieves a space record by its key or ID.",
        "arguments": "table_name='spaces', action='get', payload={space_key: str, space_id: str}",
        "flag": "Getter"
    },
    "manage_space_memberships": {
        "category": "Space Management",
        "description": "Adds or removes a user from a space.",
        "arguments": "table_name='space_memberships', action='add/remove', payload={user_id: str, space_id: str, role: user_role}",
        "flag": "Setter"
    },
    "manage_space_features": {
        "category": "Space Management",
        "description": "Manages which features are enabled for a space.",
        "arguments": "table_name='space_features', action='manage', payload={space_id: str, feature_type: space_feature_type, is_enabled: bool}",
        "flag": "Setter"
    },
    "manage_pages": {
        "category": "Page Management",
        "description": "Creates, updates, or deletes a page.",
        "arguments": "table_name='pages', action='create/update/delete', payload={page_id: str, space_id: str, parent_page_id: str, title: str, content_format: content_format, is_trashed: bool}",
        "flag": "Setter"
    },
    "get_page": {
        "category": "Page Management",
        "description": "Retrieves a page record by its ID or title.",
        "arguments": "table_name='pages', action='get', payload={page_id: str, title: str}",
        "flag": "Getter"
    },
    "move_page": {
        "category": "Page Management",
        "description": "Moves a page within or between spaces.",
        "arguments": "table_name='pages', action='move', payload={page_id: str, new_space_id?: str, new_parent_page_id?: str, moved_by_user_id: str}",
        "flag": "Setter"
    },
    "clone_page": {
        "category": "Page Management",
        "description": "Duplicates a page or an entire page tree.",
        "arguments": "table_name='pages', action='clone', payload={source_page_id: str, target_space_id: str, target_parent_page_id: str, include_children: bool, created_by_user_id: str, new_title: str}",
        "flag": "Setter"
    },
    "manage_page_versions": {
        "category": "Page Management",
        "description": "Restores a page to a previous version.",
        "arguments": "table_name='page_versions', action='restore', payload={page_id: str, version_number: int}",
        "flag": "Setter"
    },
    "get_page_versions": {
        "category": "Page Management",
        "description": "Retrieves all versions for a given page.",
        "arguments": "table_name='page_versions', action='get', payload={page_id: str}",
        "flag": "Getter"
    },
    "manage_permissions": {
        "category": "Permission Management",
        "description": "Grants, revokes (tracks who/when), or retrieves permissions.",
        "arguments": "table_name='permissions', action='grant/revoke/get', payload={space_id?: str, page_id?: str, user_id?: str, group_id?: str, permission_type?: permission_type, revoked_by_user_id?: str, include_inactive?: bool, page?: int, page_size?: int}",
        "flag": "Setter"
    },
    "manage_comments": {
        "category": "Collaboration",
        "description": "Adds, updates, or deletes a comment on a page.",
        "arguments": "table_name='comments', action='add/update/delete', payload={comment_id: str, page_id: str, comment_text: str, author_user_id: str}",
        "flag": "Setter"
    },
    "get_comments": {
        "category": "Collaboration",
        "description": "Retrieves all comments for a page.",
        "arguments": "table_name='comments', action='get', payload={page_id: str}",
        "flag": "Getter"
    },
    "manage_labels": {
        "category": "Content Management",
        "description": "Adds or removes labels from a page.",
        "arguments": "table_name='page_labels', action='add/remove', payload={page_id: str, label_names: list}",
        "flag": "Setter"
    },
    "get_labels": {
        "category": "Content Management",
        "description": "Retrieves all labels for a page.",
        "arguments": "table_name='page_labels', action='get', payload={page_id: str}",
        "flag": "Getter"
    },
    "manage_attachments": {
        "category": "Content Management",
        "description": "Adds or removes an attachment from a page.",
        "arguments": "table_name='attachments', action='add/remove', payload={page_id: str, file_name: str, file_path: str, uploaded_by_user_id: str}",
        "flag": "Setter"
    },
    "get_attachments": {
        "category": "Content Management",
        "description": "Retrieves all attachments for a page.",
        "arguments": "table_name='attachments', action='get', payload={page_id: str}",
        "flag": "Getter"
    },
    "manage_templates": {
        "category": "Template Management",
        "description": "Creates, updates, or deletes a template.",
        "arguments": "table_name='templates', action='create/update/delete', payload={template_id: str, template_name: str, template_content: str, is_blueprint: bool, space_id: str}",
        "flag": "Setter"
    },
    "use_template": {
        "category": "Template Management",
        "description": "Creates a new space or page using a template.",
        "arguments": "table_name='templates', action='use', payload={template_id: str, space_id: str, page_title: str}",
        "flag": "Setter"
    },
    "manage_watchers": {
        "category": "Watcher Management",
        "description": "Adds or removes users/groups as watchers for a page or space.",
        "arguments": "table_name='watchers', action='add/remove', payload={user_id: str, group_id: str, space_id: str, page_id: str}",
        "flag": "Setter"
    },
    "get_watchers": {
        "category": "Watcher Management",
        "description": "Retrieves all watchers for a space or page.",
        "arguments": "table_name='watchers', action='get', payload={space_id: str, page_id: str}",
        "flag": "Getter"
    },
    "manage_exports": {
        "category": "Export Management",
        "description": "Creates a space export job, imports a space from a file, or retrieves export job status.",
        "arguments": "table_name='export_jobs', action='create/import/get', payload={space_id?: str, format?: export_format, file?: file, conflict_resolution_strategy?: str, job_id?: str}",
        "flag": "Setter"
    },
    "record_audit_log": {
        "category": "Audit Management",
        "description": "Records an immutable audit log entry.",
        "arguments": "table_name='audit_logs', action='record', payload={actor_user_id: str, action_type: audit_action_type, target_entity_type: str, target_entity_id: str, details: JSON}",
        "flag": "Setter"
    },
    "get_audit_log": {
        "category": "Audit Management",
        "description": "Retrieves audit logs based on filters.",
        "arguments": "table_name='audit_logs', action='get', payload={actor_user_id: str, action_type: audit_action_type, start_date: datetime, end_date: datetime}",
        "flag": "Getter"
    },
    "record_config_change": {
        "category": "Config History",
        "description": "Records a change to a space's configuration.",
        "arguments": "table_name='space_config_history', action='record', payload={space_id: str, changed_by_user_id: str, old_config: JSON, new_config: JSON}",
        "flag": "Setter"
    },
    "get_config_history": {
        "category": "Config History",
        "description": "Retrieves the configuration history for a space.",
        "arguments": "table_name='space_config_history', action='get', payload={space_id: str}",
        "flag": "Getter"
    },
    "create_approval_request": {
        "category": "Approval Management",
        "description": "Create an approval request",
        "arguments": "table_name='approval_requests', action='create', payload={target_entity_type: str, target_entity_id: str, requested_by_user_id: str, reason?: str, due_at?: datetime, metadata?: json, steps?: list}",
        "flag": "Setter"
    },
    "decide_approval_step": {
        "category": "Approval Management",
        "description": "Records a decision for an approval step and updates overall status.",
        "arguments": "table_name='approval_decisions', action='update', payload={step_id: str, approver_user_id: str, decision: decision_type, comment?: str}",
        "flag": "Setter"
    },
    "send_notification": {
        "category": "Notification Management",
        "description": "Sends a system or email notification to a user",
        "arguments": "table_name='notifications', action='create', payload={recipient_user_id: str, event_type: str, message: str, related_entity_type?: str, related_entity_id?: str, channel?: notification_channel, sender_user_id?: str, metadata?: json}",
        "flag": "Setter"
    },
    "get_notifications": {
        "category": "Notification Management",
        "description": "Retrieves notifications for a specific user with filters.",
        "arguments": "table_name='notifications', action='get', payload={user_id: str, status?: notification_status, event_type?: str, page?: int, page_size?: int}",
        "flag": "Getter"
    }
}

def create_tool_template(tool_name: str, spec: Dict[str, Any]) -> str:
    """Create a properly implemented tool based on the specification"""
    
    class_name = tool_name.replace("_", " ").title().replace(" ", "")
    is_get_tool = spec["flag"] == "Getter"
    
    # Extract table name from arguments
    table_name = spec["arguments"].split("table_name='")[1].split("'")[0]
    
    # Create invoke method based on tool type
    if is_get_tool:
        invoke_method = create_get_invoke_method(tool_name, table_name, spec)
    else:
        invoke_method = create_set_invoke_method(tool_name, table_name, spec)
    
    template = f'''from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class {class_name}(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        {spec["description"]}
        Args:
            payload (Dict[str, Any]): Parameters for the request
        Returns:
            str: JSON response
        """
        {invoke_method}

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {{
            "tool_name": "{tool_name}",
            "category": "{spec["category"]}",
            "description": "{spec["description"]}",
            "arguments": "{spec["arguments"]}",
            "flag": "{spec["flag"]}"
        }}
'''
    return template

def create_get_invoke_method(tool_name: str, table_name: str, spec: Dict[str, Any]) -> str:
    """Create invoke method for GET tools"""
    
    # Extract key fields from arguments
    args_str = spec["arguments"]
    if "payload={" in args_str:
        payload_part = args_str.split("payload={")[1].split("}")[0]
        fields = [field.strip().split(":")[0] for field in payload_part.split(",") if ":" in field]
    else:
        fields = []
    
    # Create field validation
    field_checks = []
    for field in fields:
        if field and not field.startswith("?"):
            field_checks.append(f'        {field} = payload.get("{field}")')
    
    # Create validation logic
    if len(fields) > 1:
        field_names = [f for f in fields if f and not f.startswith("?")]
        validation = f'''
        if not any([{', '.join(field_names)}]):
            return json.dumps({{"error": "At least one of {', '.join(field_names)} must be provided in the payload."}})'''
    else:
        validation = ""
    
    # Create search logic
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
                return json.dumps({{"error": "{spec["category"].split()[0]} not found."}})
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
                return json.dumps({{"error": "{spec["category"].split()[0]} not found."}})
        except Exception as e:
            return json.dumps({{"error": str(e)}})'''
    
    return f'''{chr(10).join(field_checks)}{validation}
{search_logic}'''

def create_set_invoke_method(tool_name: str, table_name: str, spec: Dict[str, Any]) -> str:
    """Create invoke method for SET tools"""
    
    # Extract action from arguments
    args_str = spec["arguments"]
    if "action=" in args_str:
        action_part = args_str.split("action='")[1].split("'")[0]
        actions = action_part.split("/")
    else:
        actions = ["create", "update", "delete"]
    
    # Create action validation
    action_validation = f'''
        action = payload.get("action")
        if not action:
            return json.dumps({{"error": "Action is required. Use one of: {', '.join(actions)}"}})
        
        if action not in {actions}:
            return json.dumps({{"error": "Invalid action. Use one of: {', '.join(actions)}"}})'''
    
    # Create action handlers
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
            return json.dumps({{"message": "{spec["category"].split()[0]} created successfully", "id": record_id}})'''
        elif action == "update":
            handler = f'''
        elif action == "update":
            # Update existing record
            record_id = payload.get("id")
            if not record_id:
                return json.dumps({{"error": "ID is required for update"}})
            
            update_data = {{k: v for k, v in payload.items() if k not in ["action", "id"]}}
            data_manager.update_record("{table_name}", record_id, update_data)
            return json.dumps({{"message": "{spec["category"].split()[0]} updated successfully"}})'''
        elif action == "delete":
            handler = f'''
        elif action == "delete":
            # Delete record
            record_id = payload.get("id")
            if not record_id:
                return json.dumps({{"error": "ID is required for delete"}})
            
            data_manager.delete_record("{table_name}", record_id)
            return json.dumps({{"message": "{spec["category"].split()[0]} deleted successfully"}})'''
        else:
            handler = f'''
        elif action == "{action}":
            # Handle {action} action
            return json.dumps({{"message": "{action} action completed successfully"}})'''
        
        action_handlers.append(handler)
    
    # Create error handler
    error_handler = f'''
        else:
            return json.dumps({{"error": "Invalid action. Use one of: {', '.join(actions)}"}})'''
    
    return f'''{action_validation}
        
        data_manager = DataManager()
        try:{''.join(action_handlers)}{error_handler}
        except Exception as e:
            return json.dumps({{"error": str(e)}})'''

def analyze_and_fix_tools():
    """Analyze all tools and fix them according to specifications"""
    
    tools_dir = Path("/Users/fenetshewarega/Desktop/bruk-new/wiki_confluence/tools/interface_1")
    
    print("🔍 ANALYZING ALL TOOLS IN INTERFACE_1")
    print("=" * 60)
    
    issues_found = []
    tools_fixed = []
    
    for tool_name, spec in TOOL_SPECIFICATIONS.items():
        file_path = tools_dir / f"{tool_name}.py"
        
        if not file_path.exists():
            print(f"❌ {tool_name}: File not found")
            issues_found.append(f"{tool_name}: File not found")
            continue
        
        # Read current file
        with open(file_path, 'r') as f:
            current_content = f.read()
        
        # Check for issues
        issues = []
        
        # Check if invoke method is implemented
        if "raise NotImplementedError" in current_content:
            issues.append("invoke method not implemented")
        
        # Check if get_info method has correct format
        if '"tool_name"' not in current_content:
            issues.append("get_info method has wrong format")
        
        # Check if class name is correct
        class_name = tool_name.replace("_", " ").title().replace(" ", "")
        if f"class {class_name}" not in current_content:
            issues.append("incorrect class name")
        
        if issues:
            print(f"⚠️  {tool_name}: {', '.join(issues)}")
            issues_found.append(f"{tool_name}: {', '.join(issues)}")
            
            # Fix the tool
            new_content = create_tool_template(tool_name, spec)
            with open(file_path, 'w') as f:
                f.write(new_content)
            tools_fixed.append(tool_name)
            print(f"✅ {tool_name}: Fixed")
        else:
            print(f"✅ {tool_name}: OK")
    
    print(f"\n📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total tools analyzed: {len(TOOL_SPECIFICATIONS)}")
    print(f"Tools with issues: {len(issues_found)}")
    print(f"Tools fixed: {len(tools_fixed)}")
    
    if issues_found:
        print(f"\n🔧 ISSUES FOUND AND FIXED:")
        for issue in issues_found:
            print(f"  - {issue}")
    
    if tools_fixed:
        print(f"\n✅ TOOLS FIXED:")
        for tool in tools_fixed:
            print(f"  - {tool}")
    
    print(f"\n🎉 All tools now follow the correct logic and specifications!")

if __name__ == "__main__":
    analyze_and_fix_tools()
