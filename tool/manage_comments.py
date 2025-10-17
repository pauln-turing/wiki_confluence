
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json


class ManageComments(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "add":
                # flat payload: page_id, comment_text, author_user_id
                page_id = payload.get("page_id")
                comment_text = payload.get("comment_text")
                author_user_id = payload.get("author_user_id")
                comment_id = DataManager.get_next_id("comments")
                comment = {
                    "page_id": page_id,
                    "comment_text": comment_text,
                    "author_user_id": author_user_id,
                    "created_at": DataManager.get_timestamp(),
                }
                DataManager.create_record("comments", comment_id, comment)
                return json.dumps({"comment_id": comment_id, **comment})

            if action == "update":
                comment_id = payload.get("comment_id")
                if not comment_id:
                    return json.dumps({"error": "'comment_id' is required for update"})
                updates = {}
                if "comment_text" in payload:
                    updates["comment_text"] = payload.get("comment_text")
                if "author_user_id" in payload:
                    updates["author_user_id"] = payload.get("author_user_id")
                if not updates:
                    updates = payload.get("updates", {})
                updated = DataManager.update_record("comments", str(comment_id), updates)
                return json.dumps(updated)

            if action == "delete":
                comment_id = payload.get("comment_id")
                if not comment_id:
                    return json.dumps({"error": "'comment_id' is required for delete"})
                DataManager.delete_record("comments", str(comment_id))
                return json.dumps({"deleted": True, "comment_id": comment_id})

            return json.dumps({"error": "Unsupported or missing action. Use add/update/delete."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_comments",
            "category": "Collaboration",
            "description": "Adds, updates, or deletes a comment on a page.",
            "arguments": "table_name='comments', action='add/update/delete', payload={comment_id: str, page_id: str, comment_text: str, author_user_id: str}",
            "flag": "Setter"
        }
