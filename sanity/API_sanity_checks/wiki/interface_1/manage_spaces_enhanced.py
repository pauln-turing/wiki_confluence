#!/usr/bin/env python3
"""
Enhanced Manage Spaces Tool with Governance Framework
Implements comprehensive space management according to Wiki Confluence Management Policy
"""

from base import Tool
from typing import Any, Dict, Optional
from data_manager import DataManager
from governance_framework import GovernanceFramework, UserRole, PermissionType, DataClassification
import json
import datetime

class ManageSpacesEnhanced(Tool):
    def __init__(self):
        self.data_manager = DataManager()
        self.governance = GovernanceFramework()
    
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Enhanced space management with governance, validation, and audit logging.
        Supports create, update, delete operations with proper role-based access control.
        """
        try:
            # Extract operation parameters
            action = payload.get("action", "").lower()
            user_id = payload.get("user_id")
            space_key = payload.get("space_key")
            space_name = payload.get("space_name")
            space_purpose = payload.get("space_purpose", "")
            permissions = payload.get("permissions", {})
            
            if not user_id:
                return json.dumps({"error": "user_id is required"})
            
            if not action:
                return json.dumps({"error": "action is required. Use: create, update, or delete"})
            
            # Initialize governance framework
            governance = GovernanceFramework()
            
            # Validate user exists
            user_exists, user_data = governance.validate_user_exists(user_id)
            if not user_exists:
                return json.dumps({"error": "User not found"})
            
            # Route to appropriate operation
            if action == "create":
                return ManageSpacesEnhanced._create_space(governance, payload)
            elif action == "update":
                return ManageSpacesEnhanced._update_space(governance, payload)
            elif action == "delete":
                return ManageSpacesEnhanced._delete_space(governance, payload)
            else:
                return json.dumps({"error": f"Invalid action '{action}'. Use: create, update, or delete"})
                
        except Exception as e:
            return json.dumps({"error": f"Operation failed: {str(e)}"})
    
    @staticmethod
    def _create_space(governance: GovernanceFramework, payload: Dict[str, Any]) -> str:
        """Create a new space with governance validation"""
        user_id = payload.get("user_id")
        space_name = payload.get("space_name")
        space_key = payload.get("space_key")
        space_purpose = payload.get("space_purpose", "")
        permissions = payload.get("permissions", {})
        
        # Validate required fields
        if not space_name or not space_key:
            return json.dumps({"error": "space_name and space_key are required"})
        
        # Validate naming convention
        name_valid, name_msg = governance.validate_naming_convention(space_name, "space")
        if not name_valid:
            return json.dumps({"error": f"Invalid space name: {name_msg}"})
        
        # Check if space already exists
        space_exists, existing_space = governance.validate_space_exists(space_key)
        if space_exists:
            return json.dumps({"error": f"Space with key '{space_key}' already exists"})
        
        # Validate user permission
        has_permission, perm_msg = governance.validate_user_permission(
            user_id, PermissionType.CREATE_SPACE
        )
        if not has_permission:
            return json.dumps({"error": f"Permission denied: {perm_msg}"})
        
        # Check if approval is required
        requires_approval, workflow = governance.check_approval_required("create_space")
        if requires_approval:
            # Create approval request
            approval_id = governance.create_approval_request(
                requester_id=user_id,
                operation_type="create_space",
                target_entity_type="space",
                target_entity_id=space_key,
                payload=payload,
                reason=f"Create space '{space_name}' with key '{space_key}'"
            )
            return json.dumps({
                "status": "approval_required",
                "approval_request_id": approval_id,
                "message": "Space creation requires approval. Request submitted for review."
            })
        
        # Create space
        space_id = governance.data_manager.get_next_id("spaces")
        space_data = {
            "space_id": space_id,
            "space_key": space_key,
            "space_name": space_name,
            "space_purpose": space_purpose,
            "created_by_user_id": user_id,
            "created_at": datetime.datetime.now().isoformat(),
            "is_deleted": False,
            "permissions": permissions,
            "features": {
                "live_docs": True,
                "calendars": True,
                "whiteboard": True,
                "databases": True,
                "smart_links": True,
                "folders": True,
                "blogs": False
            }
        }
        
        # Save space
        governance.data_manager.create_record("spaces", space_id, space_data)
        
        # Record audit log
        governance.record_audit_log(
            actor_user_id=user_id,
            action_type="create_space",
            target_entity_type="space",
            target_entity_id=space_id,
            details={
                "space_key": space_key,
                "space_name": space_name,
                "space_purpose": space_purpose
            }
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Space '{space_name}' created successfully",
            "space_id": space_id,
            "space_key": space_key,
            "space_url": f"/spaces/{space_key}"
        })
    
    @staticmethod
    def _update_space(governance: GovernanceFramework, payload: Dict[str, Any]) -> str:
        """Update an existing space with governance validation"""
        user_id = payload.get("user_id")
        space_key = payload.get("space_key")
        space_name = payload.get("space_name")
        space_purpose = payload.get("space_purpose")
        new_permissions = payload.get("permissions")
        
        # Validate required fields
        if not space_key:
            return json.dumps({"error": "space_key is required"})
        
        # Check if space exists
        space_exists, space_data = governance.validate_space_exists(space_key)
        if not space_exists:
            return json.dumps({"error": f"Space with key '{space_key}' not found"})
        
        # Validate user permission
        has_permission, perm_msg = governance.validate_user_permission(
            user_id, PermissionType.UPDATE_SPACE, space_key
        )
        if not has_permission:
            return json.dumps({"error": f"Permission denied: {perm_msg}"})
        
        # Prepare update data
        update_data = {}
        if space_name:
            # Validate naming convention
            name_valid, name_msg = governance.validate_naming_convention(space_name, "space")
            if not name_valid:
                return json.dumps({"error": f"Invalid space name: {name_msg}"})
            update_data["space_name"] = space_name
        
        if space_purpose is not None:
            update_data["space_purpose"] = space_purpose
        
        if new_permissions:
            update_data["permissions"] = new_permissions
        
        if not update_data:
            return json.dumps({"error": "No fields to update"})
        
        # Update space
        space_id = space_data["space_id"]
        for key, value in update_data.items():
            space_data[key] = value
        
        space_data["updated_at"] = datetime.datetime.now().isoformat()
        space_data["updated_by_user_id"] = user_id
        
        governance.data_manager.update_record("spaces", space_id, space_data)
        
        # Record audit log
        governance.record_audit_log(
            actor_user_id=user_id,
            action_type="update_space",
            target_entity_type="space",
            target_entity_id=space_id,
            details={
                "space_key": space_key,
                "updated_fields": list(update_data.keys()),
                "changes": update_data
            }
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Space '{space_key}' updated successfully",
            "space_id": space_id,
            "updated_fields": list(update_data.keys())
        })
    
    @staticmethod
    def _delete_space(governance: GovernanceFramework, payload: Dict[str, Any]) -> str:
        """Delete a space with governance validation"""
        user_id = payload.get("user_id")
        space_key = payload.get("space_key")
        confirmation = payload.get("confirmation", False)
        
        # Validate required fields
        if not space_key:
            return json.dumps({"error": "space_key is required"})
        
        # Check if space exists
        space_exists, space_data = governance.validate_space_exists(space_key)
        if not space_exists:
            return json.dumps({"error": f"Space with key '{space_key}' not found"})
        
        # Validate user permission
        has_permission, perm_msg = governance.validate_user_permission(
            user_id, PermissionType.DELETE_SPACE, space_key
        )
        if not has_permission:
            return json.dumps({"error": f"Permission denied: {perm_msg}"})
        
        # Require explicit confirmation for deletion
        if not confirmation:
            return json.dumps({
                "status": "confirmation_required",
                "message": "This is a high-impact, irreversible operation. Please confirm deletion.",
                "space_name": space_data.get("space_name"),
                "space_key": space_key,
                "warning": "This will delete the space and all pages/attachments contained within"
            })
        
        # Check if approval is required
        requires_approval, workflow = governance.check_approval_required("delete_space")
        if requires_approval:
            # Create approval request
            approval_id = governance.create_approval_request(
                requester_id=user_id,
                operation_type="delete_space",
                target_entity_type="space",
                target_entity_id=space_key,
                payload=payload,
                reason=f"Delete space '{space_data.get('space_name')}' with key '{space_key}'"
            )
            return json.dumps({
                "status": "approval_required",
                "approval_request_id": approval_id,
                "message": "Space deletion requires approval. Request submitted for review."
            })
        
        # Archive space before deletion (soft delete)
        space_id = space_data["space_id"]
        space_data["is_deleted"] = True
        space_data["deleted_at"] = datetime.datetime.now().isoformat()
        space_data["deleted_by_user_id"] = user_id
        
        governance.data_manager.update_record("spaces", space_id, space_data)
        
        # Record audit log
        governance.record_audit_log(
            actor_user_id=user_id,
            action_type="delete_space",
            target_entity_type="space",
            target_entity_id=space_id,
            details={
                "space_key": space_key,
                "space_name": space_data.get("space_name"),
                "deletion_type": "soft_delete"
            }
        )
        
        return json.dumps({
            "status": "success",
            "message": f"Space '{space_key}' deleted successfully",
            "space_id": space_id,
            "deletion_type": "soft_delete"
        })
    
    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "function": {
                "name": "manage_spaces_enhanced",
                "description": "Enhanced space management with governance, validation, and audit logging. Supports create, update, delete operations with proper role-based access control.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "update", "delete"],
                            "description": "Operation to perform"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "ID of the user performing the operation"
                        },
                        "space_key": {
                            "type": "string",
                            "description": "Unique key for the space"
                        },
                        "space_name": {
                            "type": "string",
                            "description": "Display name for the space"
                        },
                        "space_purpose": {
                            "type": "string",
                            "description": "Purpose or description of the space"
                        },
                        "permissions": {
                            "type": "object",
                            "description": "Space permissions configuration"
                        },
                        "confirmation": {
                            "type": "boolean",
                            "description": "Confirmation required for delete operations"
                        }
                    },
                    "required": ["action", "user_id"]
                }
            },
            "tool_name": "manage_spaces_enhanced",
            "category": "Space Management",
            "flag": "Setter"
        }
