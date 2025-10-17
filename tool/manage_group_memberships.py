
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageGroupMemberships(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "add":
                # flat payload: user_id, group_id
                user_id = payload.get("user_id")
                group_id = payload.get("group_id")
                membership = {"user_id": user_id, "group_id": group_id}
                membership_id = DataManager.get_next_id("user_groups")
                DataManager.create_record("user_groups", membership_id, membership)
                return json.dumps({"membership_id": membership_id, **membership})

            if action == "remove":
                membership_id = payload.get("membership_id")
                if not membership_id:
                    return json.dumps({"error": "'membership_id' is required for remove"})
                DataManager.delete_record("user_groups", str(membership_id))
                return json.dumps({"deleted": True, "membership_id": membership_id})

            return json.dumps({"error": "Unsupported or missing action. Use add/remove."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_group_memberships",
            "category": "Group Management",
            "description": "Adds or removes users from a group.",
            "arguments": "table_name=\'user_groups\', action=\'add/remove\', payload={user_id: str, group_id: str}",
            "flag": "Setter"
        }

