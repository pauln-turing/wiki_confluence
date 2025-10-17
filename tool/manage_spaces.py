
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageSpaces(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "create":
                # flat payload: space_key, space_name, space_purpose, created_by_user_id
                space_key = payload.get("space_key")
                space_name = payload.get("space_name")
                space_purpose = payload.get("space_purpose")
                created_by = payload.get("created_by_user_id")
                space_id = DataManager.get_next_id("spaces")
                space = {"space_key": space_key, "space_name": space_name, "space_purpose": space_purpose, "created_by_user_id": created_by, "created_at": DataManager.get_timestamp()}
                DataManager.create_record("spaces", space_id, space)
                return json.dumps({"space_id": space_id, **space})

            if action == "update":
                space_id = payload.get("space_id")
                if not space_id:
                    return json.dumps({"error": "'space_id' is required for update"})
                updates = {}
                for k in ("space_key", "space_name", "space_purpose"):
                    if k in payload:
                        updates[k] = payload.get(k)
                if not updates:
                    updates = payload.get("updates", {})
                updated = DataManager.update_record("spaces", str(space_id), updates)
                return json.dumps(updated)

            if action == "delete":
                space_id = payload.get("space_id")
                if not space_id:
                    return json.dumps({"error": "'space_id' is required for delete"})
                DataManager.delete_record("spaces", str(space_id))
                return json.dumps({"deleted": True, "space_id": space_id})

            return json.dumps({"error": "Unsupported or missing action. Use create/update/delete."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_spaces",
            "category": "Space Management",
            "description": "Creates, updates, or deletes a space.",
            "arguments": "table_name=\'spaces\', action=\'create/update/delete\', payload={space_id: str, space_key: str, space_name: str, space_purpose: str, is_deleted: bool, created_by_user_id: str}",
            "flag": "Setter"
        }

