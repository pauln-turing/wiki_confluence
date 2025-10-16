
from base import Tool
from typing import Any
import json

class GetUser(Tool):
    @staticmethod
    def invoke(*args, **kwargs) -> Any:
        NotImplementedError("GetUser.invoke is not implemented yet.")

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_user",
            "category": "User Management",
            "description": "Retrieves a user record by ID or email.",
            "arguments": "data: Dict[str, Any], action='get', payload={user_id: str, email: str}",
        }
