
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class RecordAuditLog(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        # flat payload: actor_user_id, action_type, target_entity_type, target_entity_id, details (optional)
        try:
            actor_user_id = payload.get("actor_user_id")
            action_type = payload.get("action_type")
            target_entity_type = payload.get("target_entity_type")
            target_entity_id = payload.get("target_entity_id")
            details = payload.get("details")

            lid = DataManager.get_next_id("audit_logs")
            log = {
                "actor_user_id": actor_user_id,
                "action_type": action_type,
                "target_entity_type": target_entity_type,
                "target_entity_id": target_entity_id,
                "details": details,
                "created_at": DataManager.get_timestamp(),
            }
            DataManager.create_record("audit_logs", lid, log)
            return json.dumps({"log_id": lid, **log})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "record_audit_log",
            "category": "Audit Management",
            "description": "Records an immutable audit log entry.",
            "arguments": "table_name=\'audit_logs\', action=\'record\', payload={actor_user_id: str, action_type: audit_action_type, target_entity_type: str, target_entity_id: str, details: JSON}",
            "flag": "Setter"
        }

