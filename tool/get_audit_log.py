
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetAuditLog(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        # Support filtering by actor_user_id, action_type, start_date, end_date
        filters = {}
        for key in ("actor_user_id", "action_type"):
            if key in payload:
                filters[key] = payload[key]

        try:
            logs = DataManager.filter_records("audit_logs", filters) if filters else DataManager.get_all_records("audit_logs")
            return json.dumps(logs)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_audit_log",
            "category": "Audit Management",
            "description": "Retrieves audit logs based on filters.",
            "arguments": "table_name=\'audit_logs\', action=\'get\', payload={actor_user_id: str, action_type: audit_action_type, start_date: datetime, end_date: datetime}",
            "flag": "Getter"
        }

