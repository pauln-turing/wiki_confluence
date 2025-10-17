
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetAttachments(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        page_id = payload.get("page_id")

        if not page_id:
            return json.dumps({"error": "'page_id' must be provided in the payload."})

        try:
            attachments = DataManager.find_all_by_field("attachments", "page_id", page_id)
            return json.dumps(attachments)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_attachments",
            "category": "Content Management",
            "description": "Retrieves all attachments for a page.",
            "arguments": "table_name=\'attachments\', action=\'get\', payload={page_id: str}",
            "flag": "Getter"
        }

