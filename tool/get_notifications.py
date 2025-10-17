
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetNotifications(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        user_id = payload.get("user_id")
        filters = payload.get("filters", {})

        if not user_id:
            return json.dumps({"error": "'user_id' must be provided in the payload."})

        try:
            # Merge user_id into filters
            filters["user_id"] = user_id
            notifications = DataManager.filter_records("notifications", filters)
            return json.dumps(notifications)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_notifications",
            "category": "Notification Management",
            "description": "Retrieves notifications for a specific user with filters.",
            "arguments": "table_name=\'notifications\', action=\'get\', payload={user_id: str, status?: notification_status, event_type?: str, page?: int, page_size?: int}",
            "flag": "Getter"
        }

