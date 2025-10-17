
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageUsers(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "create":
                # flat payload: email, full_name, password, global_role, account_id
                email = payload.get("email")
                full_name = payload.get("full_name")
                password = payload.get("password")
                global_role = payload.get("global_role")
                account_id = payload.get("account_id")
                user_data = {
                    "email": email,
                    "full_name": full_name,
                    "password": password,
                    "global_role": global_role,
                    "account_id": account_id,
                    "created_at": DataManager.get_timestamp()
                }
                user_id = DataManager.get_next_id("users")
                DataManager.create_record("users", user_id, user_data)
                return json.dumps({"user_id": user_id, **user_data})

            if action == "update":
                user_id = payload.get("user_id")
                if not user_id:
                    return json.dumps({"error": "'user_id' is required for update"})
                # allow flat updates: email, full_name, password, global_role
                updates = {}
                for k in ("email", "full_name", "password", "global_role", "account_id"):
                    if k in payload:
                        updates[k] = payload.get(k)
                if not updates:
                    updates = payload.get("updates", {})
                updated = DataManager.update_record("users", str(user_id), updates)
                return json.dumps(updated)

            if action == "delete":
                user_id = payload.get("user_id")
                if not user_id:
                    return json.dumps({"error": "'user_id' is required for delete"})
                DataManager.delete_record("users", str(user_id))
                return json.dumps({"deleted": True, "user_id": user_id})

            return json.dumps({"error": "Unsupported or missing action. Use create/update/delete."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_users",
            "category": "User Management",
            "description": "Creates, updates, or deletes a user account.",
            "arguments": "table_name=\'users\', action=\'create/update/delete\', payload={user_id: str, email: str, full_name: str, password: str, global_role: user_role, account_id: str}",
            "flag": "Setter"
        }

