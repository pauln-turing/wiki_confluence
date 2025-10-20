from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json
import datetime

class SendNotification(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Sends a system or email notification to a user
        Implements proper governance, validation, and audit logging.
        """
        try:
            data_manager = DataManager()
            
            # Extract common parameters
            user_id = payload.get("user_id")
            action = payload.get("action", "").lower()
            
            # Basic validation
            if not user_id and "send_notification" not in ["get_user", "get_group", "get_space", "get_page", "get_comments", "get_labels", "get_attachments", "get_watchers", "get_audit_log", "get_config_history", "get_notifications", "get_page_versions"]:
                return json.dumps({"error": "user_id is required"})
            
            # Route to appropriate operation
            if "send_notification".startswith("manage_"):
                return SendNotification._manage_operation(data_manager, payload)
            elif "send_notification".startswith("get_"):
                return SendNotification._get_operation(data_manager, payload)
            elif "send_notification".startswith("create_"):
                return SendNotification._create_operation(data_manager, payload)
            elif "send_notification".startswith("record_"):
                return SendNotification._record_operation(data_manager, payload)
            elif "send_notification".startswith("send_"):
                return SendNotification._send_operation(data_manager, payload)
            elif "send_notification".startswith("use_"):
                return SendNotification._use_operation(data_manager, payload)
            elif "send_notification".startswith("move_"):
                return SendNotification._move_operation(data_manager, payload)
            elif "send_notification".startswith("clone_"):
                return SendNotification._clone_operation(data_manager, payload)
            elif "send_notification".startswith("decide_"):
                return SendNotification._decide_operation(data_manager, payload)
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
        
        table_name = "send_notification".replace("manage_", "")
        
        if action == "create":
            return SendNotification._create_record(data_manager, payload, table_name)
        elif action == "update":
            return SendNotification._update_record(data_manager, payload, table_name)
        elif action == "delete":
            return SendNotification._delete_record(data_manager, payload, table_name)
        else:
            return json.dumps({"error": f"Invalid action '{action}'. Use: create, update, or delete"})
    
    @staticmethod
    def _get_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        """Handle get operations"""
        table_name = "send_notification".replace("get_", "")
        
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
        table_name = "send_notification".replace("create_", "")
        return SendNotification._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _record_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "send_notification".replace("record_", "")
        return SendNotification._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _send_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "send_notification".replace("send_", "")
        return SendNotification._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _use_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "send_notification".replace("use_", "")
        return SendNotification._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _move_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "send_notification".replace("move_", "")
        return SendNotification._update_record(data_manager, payload, table_name)
    
    @staticmethod
    def _clone_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "send_notification".replace("clone_", "")
        return SendNotification._create_record(data_manager, payload, table_name)
    
    @staticmethod
    def _decide_operation(data_manager: DataManager, payload: Dict[str, Any]) -> str:
        table_name = "send_notification".replace("decide_", "")
        return SendNotification._update_record(data_manager, payload, table_name)
    
    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "function": {
                "name": "send_notification",
                "description": "Sends a system or email notification to a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "payload": {
                            "type": "object",
                            "description": "Parameters for the operation",
                            "properties": {
                                "user_id": {"type": "string", "description": "ID of the user performing the operation"},
                                "action": {"type": "string", "description": "Operation to perform"}
                            },
                            "required": ["user_id"] if True else []
                        }
                    },
                    "required": ["payload"]
                }
            },
            "tool_name": "send_notification",
            "category": "Notification Management",
            "flag": "Setter"
        }
