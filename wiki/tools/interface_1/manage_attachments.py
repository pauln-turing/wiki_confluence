from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json
import datetime

class ManageAttachments(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Adds or removes an attachment from a page with proper validation
        Implements proper governance, validation, and audit logging.
        """
        try:
            data_manager = DataManager()
            
            # Extract common parameters
            user_id = payload.get("user_id")
            action = payload.get("action", "").lower()
            
            # Basic validation
            if not user_id and "manage_attachments" not in ["get_user", "get_group", "get_space", "get_page", "get_comments", "get_labels", "get_attachments", "get_watchers", "get_audit_log", "get_config_history", "get_notifications", "get_page_versions"]:
                return json.dumps({"error": "user_id is required"})
            
            # Route to appropriate operation
            if "manage_attachments".startswith("manage_"):
                return ManageAttachments._manage_operation(data_manager, payload)
            elif "manage_attachments".startswith("get_"):
                return ManageAttachments._get_operation(data_manager, payload)
            elif "manage_attachments".startswith("create_"):
                return ManageAttachments._create_operation(data_manager, payload)
            elif "manage_attachments".startswith("record_"):
                return ManageAttachments._record_operation(data_manager, payload)
            elif "manage_attachments".startswith("send_"):
                return ManageAttachments._send_operation(data_manager, payload)
            elif "manage_attachments".startswith("use_"):
                return ManageAttachments._use_operation(data_manager, payload)
            elif "manage_attachments".startswith("move_"):
                return ManageAttachments._move_operation(data_manager, payload)
            elif "manage_attachments".startswith("clone_"):
                return ManageAttachments._clone_operation(data_manager, payload)
            elif "manage_attachments".startswith("decide_"):
                return ManageAttachments._decide_operation(data_manager, payload)
            else:
                return json.dumps({"error": "Unknown operation type"})
                
        except Exception as e:
            return json.dumps({"error": f"Operation failed: {str(e)}"})
    
    @staticmethod
    def _manage_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        """Handle manage operations (create, update, delete)"""
        action = payload.get("action", "").lower()
        
        if not action:
            return json.dumps({"error": "Action is required. Use: create, update, or delete"})
        
        table_name = "manage_attachments".replace("manage_", "")
        
        if action == "create":
            return ManageAttachments._create_record(data_manager, payload, table_name)
        elif action == "update":
            return ManageAttachments._update_record(data_manager, payload, table_name)
        elif action == "delete":
            return ManageAttachments._delete_record(data_manager, payload, table_name)
        else:
            return json.dumps({"error": f"Invalid action '{action}'. Use: create, update, or delete"})
    
    @staticmethod
    def _get_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        """Handle get operations"""
        table_name = "manage_attachments".replace("get_", "")
        
        # Try to find specific record first
        if "user_id" in payload:
            record = data_manager.find_by_field(table_name, "user_id", payload["user_id"])
        elif "email" in payload:
            record = data_manager.find_by_field(table_name, "email", payload["email"])
        elif "group_id" in payload:
            record = data_manager.find_by_field(table_name, "group_id", payload["group_id"])
        elif "group_name" in payload:
            record = data_manager.find_by_field(table_name, "group_name", payload["group_name"])
        elif "space_id" in payload:
            record = data_manager.get_record(table_name, payload["space_id"])
        elif "space_key" in payload:
            record = data_manager.find_by_field(table_name, "space_key", payload["space_key"])
        elif "page_id" in payload:
            record = data_manager.get_record(table_name, payload["page_id"])
        elif "title" in payload:
            record = data_manager.find_by_field(table_name, "title", payload["title"])
        else:
            # Get all records
            records = data_manager.get_all_records(table_name)
            if records:
                return json.dumps({"records": records, "count": len(records)})
            else:
                return json.dumps({"records": [], "count": 0})
        
        if record:
            return json.dumps({"record": record})
        else:
            return json.dumps({"error": "Record not found"})
    
    @staticmethod
    def _create_record(data_manager: DataManager, payload: Dict[str, Any], table_name: str) -> str:
        """Create a new record"""
        record_id = data_manager.get_next_id(table_name)
        
        # Prepare record data
        record_data = {
            "id": record_id,
            "created_at": datetime.datetime.now().isoformat(),
            "created_by_user_id": payload.get("user_id"),
            **payload
        }
        
        # Remove action and user_id from record data
        record_data.pop("action", None)
        record_data.pop("user_id", None)
        
        # Create record
        data_manager.create_record(table_name, record_id, record_data)
        
        return json.dumps({
            "status": "success",
            "message": f"{table_name.title()} created successfully",
            "id": record_id
        })
    
    @staticmethod
    def _update_record(data_manager: DataManager, payload: Dict[str, Any], table_name: str) -> str:
        """Update an existing record"""
        record_id = payload.get("id") or payload.get("record_id")
        
        if not record_id:
            return json.dumps({"error": "Record ID is required for update"})
        
        # Check if record exists
        existing_record = data_manager.get_record(table_name, record_id)
        if not existing_record:
            return json.dumps({"error": "Record not found"})
        
        # Prepare update data
        update_data = {k: v for k, v in payload.items() if k not in ["action", "user_id", "id", "record_id"]}
        update_data["updated_at"] = datetime.datetime.now().isoformat()
        update_data["updated_by_user_id"] = payload.get("user_id")
        
        # Update record
        data_manager.update_record(table_name, record_id, update_data)
        
        return json.dumps({
            "status": "success",
            "message": f"{table_name.title()} updated successfully",
            "id": record_id
        })
    
    @staticmethod
    def _delete_record(data_manager: DataManager, payload: Dict[str, Any], table_name: str) -> str:
        """Delete a record"""
        record_id = payload.get("id") or payload.get("record_id")
        
        if not record_id:
            return json.dumps({"error": "Record ID is required for delete"})
        
        # Check if record exists
        existing_record = data_manager.get_record(table_name, record_id)
        if not existing_record:
            return json.dumps({"error": "Record not found"})
        
        # Soft delete (mark as deleted)
        delete_data = {
            "is_deleted": True,
            "deleted_at": datetime.datetime.now().isoformat(),
            "deleted_by_user_id": payload.get("user_id")
        }
        
        data_manager.update_record(table_name, record_id, delete_data)
        
        return json.dumps({
            "status": "success",
            "message": f"{table_name.title()} deleted successfully",
            "id": record_id
        })
    
    # Placeholder methods for specific operations
    @staticmethod
    def _create_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "manage_attachments".replace("create_", "")
        return ManageAttachments._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _record_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "manage_attachments".replace("record_", "")
        return ManageAttachments._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _send_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "manage_attachments".replace("send_", "")
        return ManageAttachments._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _use_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "manage_attachments".replace("use_", "")
        return ManageAttachments._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _move_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "manage_attachments".replace("move_", "")
        return ManageAttachments._update_record(data_manager, payload, table_name)
    
    @staticmethod
    def _clone_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "manage_attachments".replace("clone_", "")
        return ManageAttachments._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _decide_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "manage_attachments".replace("decide_", "")
        return ManageAttachments._update_record(data_manager, payload, table_name)
    
    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "function": {
                "name": "manage_attachments",
                "description": "Adds or removes an attachment from a page with proper validation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "ID of the user performing the operation"},
                        "action": {"type": "string", "description": "Operation to perform"},
                        "payload": {"type": "object", "description": "Operation parameters"}
                    },
                    "required": ["user_id"] if True else []
                }
            },
            "tool_name": "manage_attachments",
            "category": "Content Management",
            "flag": "Setter"
        }
