import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class UpdatePayment(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pay_id = payload.get("payment_id") or payload.get("id")
        updates = payload.get("updates") or payload.get("data")
        if not pay_id or not isinstance(updates, dict):
            return {"success": False, "error": "missing_id_or_updates"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            pays = db.setdefault("payments", [])
            for p in pays:
                if p.get("payment_id") == pay_id:
                    p.update(updates)
                    p["updated_at"] = ts
                    db.setdefault("audit_log", []).append({"audit_id": f"audit_{pay_id}", "entity_type": "payment", "entity_id": pay_id, "action_performed": "updated", "timestamp": ts})
                    return {"success": True, "payment": p}
            return {"success": False, "error": "not_found"}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "payments.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            pays = raw
        elif isinstance(raw, dict):
            pays = list(raw.values())
        else:
            return {"success": False, "error": "bad_data"}

        for p in pays:
            if p.get("payment_id") == pay_id:
                p.update(updates)
                p["updated_at"] = ts
                try:
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(pays, f, indent=2)
                    os.replace(tmp, path)
                except Exception as e:
                    return {"success": False, "error": "write_error", "details": str(e)}

                audit_entry = {"audit_id": f"audit_{pay_id}", "entity_type": "payment", "entity_id": pay_id, "action_performed": "updated", "timestamp": ts}
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
    def invoke(data: Dict[str, Any], payment_id: str, updates: Dict[str, Any]) -> str:
        try:
            res = UpdatePayment._invoke_internal({"payment_id": payment_id, "updates": updates}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "update_payment", "description": "Update a payment record.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "payment_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["data", "payment_id", "updates"]}}}
