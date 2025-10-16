import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class ExecuteExternalPayment(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payment_id = payload.get("payment_id") or payload.get("id")
        if not payment_id:
            return {"success": False, "error": "missing_payment_id"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        # For safety, external execution is simulated: mark status executed
        if db is not None:
            pays = db.setdefault("payments", [])
            for p in pays:
                if p.get("payment_id") == payment_id:
                    p["status"] = "executed_external"
                    p["executed_at"] = ts
                    db.setdefault("audit_log", []).append({"audit_id": f"audit_{payment_id}", "entity_type": "payment", "entity_id": payment_id, "action_performed": "executed_external", "timestamp": ts})
                    return {"success": True, "payment": p}
            return {"success": False, "error": "not_found"}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "payments.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            else:
                return {"success": False, "error": "not_found"}
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            pays = raw
        elif isinstance(raw, dict):
            pays = list(raw.values())
        else:
            return {"success": False, "error": "not_found"}

        for p in pays:
            if p.get("payment_id") == payment_id:
                p["status"] = "executed_external"
                p["executed_at"] = ts
                try:
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(pays, f, indent=2)
                    os.replace(tmp, path)
                except Exception as e:
                    return {"success": False, "error": "write_error", "details": str(e)}

                audit_entry = {"audit_id": f"audit_{payment_id}", "entity_type": "payment", "entity_id": payment_id, "action_performed": "executed_external", "timestamp": ts}
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

                return {"success": True, "payment": p, "audit_entry": audit_entry}

        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], payment_request: Dict[str, Any]) -> str:
        try:
            res = ExecuteExternalPayment._invoke_internal({"payment_request": payment_request}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "execute_external_payment", "description": "Execute an external payment (simulated).", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "payment_request": {"type": "dict"}}, "required": ["data", "payment_request"]}}}
