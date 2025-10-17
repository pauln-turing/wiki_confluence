
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class MovePage(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        page_id = payload.get("page_id")
        target_parent = payload.get("target_parent_page_id")
        try:
            page = DataManager.get_record("pages", str(page_id))
            if not page:
                return json.dumps({"error": "Page not found"})
            updated = DataManager.update_record("pages", str(page_id), {"parent_page_id": target_parent, "updated_at": DataManager.get_timestamp()})
            return json.dumps(updated)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "move_page",
            "category": "Page Management",
            "description": "Moves a page within or between spaces.",
            "arguments": "table_name=\'pages\', action=\'move\', payload={page_id: str, new_space_id?: str, new_parent_page_id?: str, moved_by_user_id: str}",
            "flag": "Setter"
        }

