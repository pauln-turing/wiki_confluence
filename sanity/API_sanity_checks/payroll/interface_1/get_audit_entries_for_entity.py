import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetAuditEntriesForEntity(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        entity_type = payload.get("entity_type")
        entity_id = payload.get("entity_id")

        if db is not None:
            audits = db.get("audit_logs", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "audit_logs.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                audits = raw
            elif isinstance(raw, dict):
                audits = list(raw.values())
            else:
                audits = []

        results = [a for a in audits if (not entity_type or a.get("entity_type") == entity_type) and (not entity_id or a.get("entity_id") == entity_id)]
        return {"success": True, "audit_entries": results}

    @staticmethod
    def invoke(data: Dict[str, Any], entity_type: str | None = None, entity_id: str | None = None) -> str:
        try:
            res = GetAuditEntriesForEntity._invoke_internal({"entity_type": entity_type, "entity_id": entity_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_audit_entries_for_entity", "description": "Return audit entries for an entity.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "entity_type": {"type": ["string","null"]}, "entity_id": {"type": ["string","null"]}}, "required": ["data"]}}}
