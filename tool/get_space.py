
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetSpace(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        space_id = payload.get("space_id")
        space_key = payload.get("space_key")

        if not space_id and not space_key:
            return json.dumps({"error": "Either 'space_id' or 'space_key' must be provided in the payload."})

        try:
            if space_id:
                space = DataManager.get_record("spaces", str(space_id))
            else:
                space = DataManager.find_by_field("spaces", "space_key", space_key)

            if space:
                return json.dumps(space)
            return json.dumps({"error": "Space not found."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_space",
            "category": "Space Management",
            "description": "Retrieves a space record by its key or ID.",
            "arguments": "table_name=\'spaces\', action=\'get\', payload={space_key: str, space_id: str}",
            "flag": "Getter"
        }

