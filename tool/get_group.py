
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetGroup(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        group_id = payload.get("group_id")
        group_name = payload.get("group_name")

        if not group_id and not group_name:
            return json.dumps({"error": "Either 'group_id' or 'group_name' must be provided in the payload."})

        try:
            if group_id:
                group = DataManager.get_record("groups", group_id)
            else:
                group = DataManager.find_by_field("groups", "group_name", group_name)

            if group:
                return json.dumps(group)
            return json.dumps({"error": "Group not found."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_group",
            "category": "Group Management",
            "description": "Retrieves a group record by ID or name.",
            "arguments": "table_name=\'groups\', action=\'get\', payload={group_id: str, group_name: str}",
            "flag": "Getter"
        }

