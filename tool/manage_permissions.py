
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManagePermissions(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "grant":
                # flat payload: space_id (opt), page_id (opt), user_id (opt), group_id (opt), permission_type
                space_id = payload.get("space_id")
                page_id = payload.get("page_id")
                user_id = payload.get("user_id")
                group_id = payload.get("group_id")
                permission_type = payload.get("permission_type")
                perm = {
                    "space_id": space_id,
                    "page_id": page_id,
                    "user_id": user_id,
                    "group_id": group_id,
                    "permission_type": permission_type,
                    "granted_at": DataManager.get_timestamp(),
                }
                perm_id = DataManager.get_next_id("permissions")
                DataManager.create_record("permissions", perm_id, perm)
                return json.dumps({"permission_id": perm_id, **perm})

            if action == "revoke":
                permission_id = payload.get("permission_id")
                # mark as revoked or delete
                reason = payload.get("reason")
                if permission_id:
                    updated = DataManager.update_record("permissions", permission_id, {"revoked": True, "revoked_reason": reason, "revoked_at": DataManager.get_timestamp()})
                    return json.dumps(updated)
                return json.dumps({"error": "permission_id required for revoke"})

            if action == "get":
                filters = payload.get("filters", {})
                perms = DataManager.filter_records("permissions", filters)
                return json.dumps(perms)

            return json.dumps({"error": "Unsupported or missing action. Use grant/revoke/get."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_permissions",
            "category": "Permission Management",
            "description": "	Grants, revokes (tracks who/when), or retrieves permissions.",
            "arguments": "table_name=\'permissions\', action=\'grant/revoke/get\', payload={space_id?: str, page_id?: str, user_id?: str, group_id?: str, permission_type?: permission_type, revoked_by_user_id?: str, include_inactive?: bool, page?: int, page_size?: int}",
            "flag": "Setter"
        }

