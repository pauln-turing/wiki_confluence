
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageGroups(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "create":
                # flat payload: group_name, members?
                group_name = payload.get("group_name")
                members = payload.get("members", [])
                group_data = {"group_name": group_name, "members": members}
                group_id = DataManager.get_next_id("groups")
                DataManager.create_record("groups", group_id, group_data)
                return json.dumps({"group_id": group_id, **group_data})

            if action == "update":
                group_id = payload.get("group_id")
                if not group_id:
                    return json.dumps({"error": "'group_id' is required for update"})
                updates = {}
                if "group_name" in payload:
                    updates["group_name"] = payload.get("group_name")
                if "members" in payload:
                    updates["members"] = payload.get("members")
                if not updates:
                    updates = payload.get("updates", {})
                updated = DataManager.update_record("groups", str(group_id), updates)
                return json.dumps(updated)

            if action == "delete":
                group_id = payload.get("group_id")
                if not group_id:
                    return json.dumps({"error": "'group_id' is required for delete"})
                DataManager.delete_record("groups", str(group_id))
                return json.dumps({"deleted": True, "group_id": group_id})

            return json.dumps({"error": "Unsupported or missing action. Use create/update/delete."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_groups",
            "category": "Group Management",
            "description": "Creates, updates, or deletes a user group.",
            "arguments": "table_name=\'groups\', action='create/update/delete', payload={group_id: str, group_name: str}",
            "flag": "Setter"
        }

