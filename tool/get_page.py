
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetPage(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        page_id = payload.get("page_id")
        title = payload.get("title")

        if not page_id and not title:
            return json.dumps({"error": "Either 'page_id' or 'title' must be provided in the payload."})

        try:
            if page_id:
                page = DataManager.get_record("pages", str(page_id))
            else:
                page = DataManager.find_by_field("pages", "title", title)

            if page:
                return json.dumps(page)
            return json.dumps({"error": "Page not found."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_page",
            "category": "Page Management",
            "description": "Retrieves a page record by its ID or title.",
            "arguments": "table_name=\'pages\', action=\'get\', payload={page_id: str, title: str}",
            "flag": "Getter"
        }

