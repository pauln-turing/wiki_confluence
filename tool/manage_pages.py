
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json


class ManagePages(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "create":
                # flat payload: space_id, parent_page_id, title, content_format, content, created_by_user_id
                space_id = payload.get("space_id")
                parent_page_id = payload.get("parent_page_id")
                title = payload.get("title")
                content_format = payload.get("content_format")
                content = payload.get("content")
                created_by = payload.get("created_by_user_id")
                page_id = DataManager.get_next_id("pages")
                page = {
                    "space_id": space_id,
                    "parent_page_id": parent_page_id,
                    "title": title,
                    "content_format": content_format,
                    "content": content,
                    "created_by_user_id": created_by,
                    "created_at": DataManager.get_timestamp()
                }
                DataManager.create_record("pages", page_id, page)
                return json.dumps({"page_id": page_id, **page})

            if action == "update":
                page_id = payload.get("page_id")
                if not page_id:
                    return json.dumps({"error": "'page_id' is required for update"})
                updates = {}
                for k in ("space_id", "parent_page_id", "title", "content_format", "content", "is_trashed", "is_published"):
                    if k in payload:
                        updates[k] = payload.get(k)
                if not updates:
                    updates = payload.get("updates", {})
                updated = DataManager.update_record("pages", str(page_id), updates)
                return json.dumps(updated)

            if action == "delete":
                page_id = payload.get("page_id")
                if not page_id:
                    return json.dumps({"error": "'page_id' is required for delete"})
                DataManager.delete_record("pages", str(page_id))
                return json.dumps({"deleted": True, "page_id": page_id})

            return json.dumps({"error": "Unsupported or missing action. Use create/update/delete."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_pages",
            "category": "Page Management",
            "description": "Creates, updates, or deletes a page.",
            "arguments": "table_name='pages', action='create/update/delete', payload={page_id: str, space_id: str, parent_page_id: str, title: str, content_format: content_format, is_trashed: bool}",
            "flag": "Setter"
        }

