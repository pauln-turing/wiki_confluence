
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageWatchers(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "add":
                # flat payload: user_id, group_id, space_id, page_id
                user_id = payload.get("user_id")
                group_id = payload.get("group_id")
                space_id = payload.get("space_id")
                page_id = payload.get("page_id")
                watcher = {
                    "user_id": user_id,
                    "group_id": group_id,
                    "space_id": space_id,
                    "page_id": page_id,
                    "created_at": DataManager.get_timestamp(),
                }
                wid = DataManager.get_next_id("watchers")
                DataManager.create_record("watchers", wid, watcher)
                return json.dumps({"watcher_id": wid, **watcher})

            if action == "remove":
                watcher_id = payload.get("watcher_id")
                if not watcher_id:
                    return json.dumps({"error": "'watcher_id' is required for remove"})
                DataManager.delete_record("watchers", str(watcher_id))
                return json.dumps({"deleted": True, "watcher_id": watcher_id})

            return json.dumps({"error": "Unsupported or missing action. Use add/remove."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_watchers",
            "category": "Watcher Management",
            "description": "Adds or removes users/groups as watchers for a page or space.",
            "arguments": "table_name=\'watchers\', action='add/remove', payload={user_id: str, group_id: str, space_id: str, page_id: str}",
            "flag": "Setter"
        }

