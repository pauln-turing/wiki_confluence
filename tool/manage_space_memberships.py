
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageSpaceMemberships(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "add":
                # flat payload: user_id, space_id, role
                user_id = payload.get("user_id")
                space_id = payload.get("space_id")
                role = payload.get("role")
                membership = {"user_id": user_id, "space_id": space_id, "role": role, "created_at": DataManager.get_timestamp()}
                mid = DataManager.get_next_id("space_memberships")
                DataManager.create_record("space_memberships", mid, membership)
                return json.dumps({"membership_id": mid, **membership})

            if action == "remove":
                membership_id = payload.get("membership_id")
                if not membership_id:
                    return json.dumps({"error": "'membership_id' is required for remove"})
                DataManager.delete_record("space_memberships", str(membership_id))
                return json.dumps({"deleted": True, "membership_id": membership_id})

            return json.dumps({"error": "Unsupported or missing action. Use add/remove."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_space_memberships",
            "category": "Space Management",
            "description": "Adds or removes a user from a space.",
            "arguments": "table_name=\'space_memberships\', action=\'add/remove\', payload={user_id: str, space_id: str, role: user_role}",
            "flag": "Setter"
        }

