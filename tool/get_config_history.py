
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetConfigHistory(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        space_id = payload.get("space_id")

        if not space_id:
            return json.dumps({"error": "'space_id' must be provided in the payload."})

        try:
            history = DataManager.find_all_by_field("space_config_history", "space_id", space_id)
            return json.dumps(history)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_config_history",
            "category": "Config History",
            "description": "Retrieves the configuration history for a space.",
            "arguments": "table_name=\'space_config_history\', action=\'get\', payload={space_id: str}",
            "flag": "Getter"
        }

