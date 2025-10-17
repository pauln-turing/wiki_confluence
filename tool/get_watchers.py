
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetWatchers(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        space_id = payload.get("space_id")
        page_id = payload.get("page_id")

        try:
            if page_id:
                watchers = DataManager.find_all_by_field("watchers", "page_id", page_id)
            elif space_id:
                watchers = DataManager.find_all_by_field("watchers", "space_id", space_id)
            else:
                return json.dumps({"error": "Either 'space_id' or 'page_id' must be provided."})

            return json.dumps(watchers)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_watchers",
            "category": "Watcher Management",
            "description": "Retrieves all watchers for a space or page.",
            "arguments": "table_name=\'watchers\', action=\'get\', payload={space_id: str, page_id: str}",
            "flag": "Getter"
        }

