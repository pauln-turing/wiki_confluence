
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetPageVersions(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        page_id = payload.get("page_id")

        if not page_id:
            return json.dumps({"error": "'page_id' must be provided in the payload."})

        try:
            versions = DataManager.find_all_by_field("page_versions", "page_id", page_id)
            return json.dumps(versions)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_page_versions",
            "category": "Page Management",
            "description": "Retrieves all versions for a given page.",
            "arguments": "table_name=\'page_versions\', action=\'get\', payload={page_id: str}",
            "flag": "Getter"
        }

