
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetLabels(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        page_id = payload.get("page_id")

        if not page_id:
            return json.dumps({"error": "'page_id' must be provided in the payload."})

        try:
            labels = DataManager.find_all_by_field("page_labels", "page_id", page_id)
            return json.dumps(labels)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_labels",
            "category": "Content Management",
            "description": "Retrieves all labels for a page.",
            "arguments": "table_name=\'page_labels\', action=\'get\', payload={page_id: str}",
            "flag": "Getter"
        }

