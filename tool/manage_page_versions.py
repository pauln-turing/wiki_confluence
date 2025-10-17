
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManagePageVersions(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "restore":
                page_id = payload.get("page_id")
                version_number = payload.get("version_number")
                # find version
                versions = DataManager.find_all_by_field("page_versions", "page_id", page_id)
                target = None
                for v in versions:
                    if v.get("version_number") == version_number:
                        target = v
                        break
                if not target:
                    return json.dumps({"error": "Version not found"})
                if not page_id:
                    return json.dumps({"error": "'page_id' is required for restore"})
                # update page content
                updated = DataManager.update_record("pages", str(page_id), {"content": target.get("content"), "restored_from_version": version_number, "updated_at": DataManager.get_timestamp()})
                return json.dumps(updated)

            return json.dumps({"error": "Unsupported or missing action. Use restore."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_page_versions",
            "category": "Page Management",
            "description": "Restores a page to a previous version.",
            "arguments": "table_name=\'page_versions\', action='restore', payload={page_id: str, version_number: int}",
            "flag": "Setter"
        }

