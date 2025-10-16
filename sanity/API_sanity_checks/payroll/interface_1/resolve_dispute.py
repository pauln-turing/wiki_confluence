import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class ResolveDispute(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        dispute_id = payload.get("dispute_id") or payload.get("id")
        resolution = payload.get("resolution")
        if not dispute_id:
            return {"success": False, "error": "missing_dispute_id"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            disputes = db.setdefault("disputes", [])
            for d in disputes:
                if d.get("dispute_id") == dispute_id:
                    d["status"] = "resolved"
                    d["resolution"] = resolution
                    d["resolved_at"] = ts
                    db.setdefault("audit_log", []).append({"audit_id": f"audit_{dispute_id}", "entity_type": "dispute", "entity_id": dispute_id, "action_performed": "resolved", "timestamp": ts})
                    return {"success": True, "dispute": d}
            return {"success": False, "error": "not_found"}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "disputes.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            else:
                return {"success": False, "error": "not_found"}
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            disputes = raw
        elif isinstance(raw, dict):
            disputes = list(raw.values())
        else:
            return {"success": False, "error": "not_found"}

        for d in disputes:
            if d.get("dispute_id") == dispute_id:
                d["status"] = "resolved"
                d["resolution"] = resolution
                d["resolved_at"] = ts
                try:
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(disputes, f, indent=2)
                    os.replace(tmp, path)
                except Exception as e:
                    return {"success": False, "error": "write_error", "details": str(e)}

                audit_entry = {"audit_id": f"audit_{dispute_id}", "entity_type": "dispute", "entity_id": dispute_id, "action_performed": "resolved", "timestamp": ts}
                try:
                    audit_path = os.path.join(data_dir, "audit_log.json")
                    if os.path.exists(audit_path):
                        with open(audit_path, "r", encoding="utf-8") as f:
                            raw_a = json.load(f)
                    else:
                        raw_a = []
                    if isinstance(raw_a, list):
                        audit = raw_a
                    elif isinstance(raw_a, dict):
                        audit = list(raw_a.values())
                    else:
                        audit = []
                    audit.append(audit_entry)
                    tmpa = audit_path + ".tmp"
                    with open(tmpa, "w", encoding="utf-8") as f:
                        json.dump(audit, f, indent=2)
                    os.replace(tmpa, audit_path)
                except Exception:
                    pass

                return {"success": True, "dispute": d, "audit_entry": audit_entry}

        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], dispute_id: str, resolution: Dict[str, Any]) -> str:
        try:
            res = ResolveDispute._invoke_internal({"dispute_id": dispute_id, "resolution": resolution}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "resolve_dispute", "description": "Resolve a dispute.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "dispute_id": {"type": "string"}, "resolution": {"type": "dict"}}, "required": ["data", "dispute_id", "resolution"]}}}
