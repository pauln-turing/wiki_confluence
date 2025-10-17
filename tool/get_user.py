
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetUser(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        user_id = payload.get("user_id")
        email = payload.get("email")

        if not user_id and not email:
            return json.dumps({"error": "Either 'user_id' or 'email' must be provided in the payload."})

        try:
            if user_id:
                user = DataManager.get_record("users", str(user_id))
            else:
                user = DataManager.find_by_field("users", "email", email)

            if user:
                return json.dumps(user)
            return json.dumps({"error": "User not found."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_user",
            "category": "User Management",
            "description": "Retrieves a user record by ID or email.",
            "arguments": "table_name=\'users\', action=\'get\', payload={user_id: str, email: str}",
            "flag": "Getter"
        }

