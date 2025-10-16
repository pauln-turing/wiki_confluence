import json
import os
from typing import Any, Dict, Optional
from base import Tool


class AddAuditLogsEntry(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        audit_id = payload.get("audit_id")
        entity_type = payload.get("entity_type")
        entity_id = payload.get("entity_id")
        action_performed = payload.get("action_performed")
        performed_by = payload.get("performed_by")
        role = payload.get("role")
        timestamp = payload.get("timestamp")
        details = payload.get("details")

        if not audit_id or not entity_type or not entity_id or not action_performed:
            return {"success": False, "error": "missing_fields"}

        entry = {
            "audit_id": audit_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action_performed": action_performed,
            "performed_by": performed_by,
            "role": role,
            "timestamp": timestamp,
            "details": details,
        }

        if db is not None:
            db.setdefault("audit_logs", {})[audit_id] = entry
            return {"success": True, "audit_entry": entry}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "audit_logs.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            else:
                raw = {}
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, dict):
            table = raw
        else:
            table = {}

        table[audit_id] = entry
        try:
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(table, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        return {"success": True, "audit_entry": entry}

    @staticmethod
    def invoke(data: Dict[str, Any], entry: Dict[str, Any]) -> str:
        """
        Approvals-style wrapper: expects an in-memory `data` dict and the audit entry dict.
        """
        try:
            # allow callers to pass the full entry or individual fields
            if isinstance(entry, dict) and entry.get("audit_id"):
                payload = entry
            else:
                payload = entry
            res = AddAuditLogsEntry._invoke_internal(payload, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "add_audit_logs_entry",
                "description": "Add an audit log entry. Expects in-memory data dict and an audit entry dict.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "dict"},
                        "entry": {"type": "dict"}
                    },
                    "required": ["data", "entry"]
                }
            }
        }
