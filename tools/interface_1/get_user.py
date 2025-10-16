
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetUser(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Retrieves a user record by ID or email.
        Args:
            payload (Dict[str, Any]): A dictionary containing the following keys:
                - user_id (str, optional): The ID of the user to retrieve.
                - email (str, optional): The email of the user to retrieve.
        Returns:
            Dict[str, Any]: A dictionary representing the user record, or an error message if not found.
        """
        user_id = payload.get("user_id")
        email = payload.get("email")

        if not user_id and not email:
            return json.dumps({"error": "Either 'user_id' or 'email' must be provided in the payload."})

        data_manager = DataManager()
        if user_id:
            user = data_manager.get_record("users", user_id)
        else:
            user = data_manager.find_by_field("users", "email", email)

        if user:
            return json.dumps(user)
        else:
            return json.dumps({"error": "User not found."})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_user",
            "category": "User Management",
            "description": "Retrieves a user record by ID or email.",
            "arguments": "table_name=\'users\', action=\'get\', payload={user_id: str, email: str}",
            "flag": "Getter"
        }

