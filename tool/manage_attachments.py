
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageAttachments(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "add":
                # Expect flat fields in payload: page_id, file_name, file_path, uploaded_by_user_id
                page_id = payload.get("page_id")
                file_name = payload.get("file_name")
                file_path = payload.get("file_path")
                uploaded_by = payload.get("uploaded_by_user_id")
                att = {
                    "page_id": page_id,
                    "file_name": file_name,
                    "file_path": file_path,
                    "uploaded_by_user_id": uploaded_by,
                    "uploaded_at": DataManager.get_timestamp()
                }
                att_id = DataManager.get_next_id("attachments")
                DataManager.create_record("attachments", att_id, att)
                return json.dumps({"attachment_id": att_id, **att})

            if action == "remove":
                attachment_id = payload.get("attachment_id")
                if not attachment_id:
                    return json.dumps({"error": "'attachment_id' is required for remove"})
                DataManager.delete_record("attachments", str(attachment_id))
                return json.dumps({"deleted": True, "attachment_id": attachment_id})

            return json.dumps({"error": "Unsupported or missing action. Use add/remove."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_attachments",
            "category": "Content Management",
            "description": "Adds or removes an attachment from a page.",
            "arguments": "table_name=\'attachments\', action=\'add/remove\', payload={page_id: str, file_name: str, file_path: str, uploaded_by_user_id: str}",
            "flag": "Setter"
        }

