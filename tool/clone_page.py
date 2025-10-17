
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ClonePage(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        source_page_id = payload.get("source_page_id")
        target_space_id = payload.get("target_space_id")
        new_title = payload.get("new_title")
        try:
            if not source_page_id:
                return json.dumps({"error": "'source_page_id' is required"})
            src = DataManager.get_record("pages", str(source_page_id))
            if not src:
                return json.dumps({"error": "Source page not found"})
            nid = DataManager.get_next_id("pages")
            title_base = src.get("title") or "Untitled"
            title_value = new_title if new_title is not None else f"{title_base} (clone)"
            space_value = target_space_id if target_space_id is not None else src.get("space_id")
            new_page = {"title": title_value, "content": src.get("content"), "space_id": space_value, "created_at": DataManager.get_timestamp()}
            DataManager.create_record("pages", nid, new_page)
            return json.dumps({"page_id": nid, **new_page})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "clone_page",
            "category": "Page Management",
            "description": "Duplicates a page or an entire page tree.",
            "arguments": "table_name=\'pages\', action=\'clone\', payload={source_page_id: str, target_space_id: str, target_parent_page_id: str, include_children: bool,created_by_user_id:str, new_title:str}",
            "flag": "Setter"
        }

