
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class RecordConfigChange(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        # flat payload: space_id, changed_by_user_id, old_config, new_config, reason (optional), details (optional)
        try:
            space_id = payload.get("space_id")
            changed_by = payload.get("changed_by_user_id")
            old_config = payload.get("old_config")
            new_config = payload.get("new_config")
            reason = payload.get("reason")
            details = payload.get("details")

            cid = DataManager.get_next_id("space_config_history")
            change = {
                "space_id": space_id,
                "changed_by_user_id": changed_by,
                "old_config": old_config,
                "new_config": new_config,
                "reason": reason,
                "details": details,
                "recorded_at": DataManager.get_timestamp(),
            }
            DataManager.create_record("space_config_history", cid, change)
            return json.dumps({"change_id": cid, **change})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "record_config_change",
            "category": "Config History",
            "description": "Records a change to a space's configuration.",
            "arguments": "table_name='space_config_history', action='record', payload={space_id: str, changed_by_user_id: str, old_config: JSON, new_config: JSON}",
            "flag": "Setter"
        }

