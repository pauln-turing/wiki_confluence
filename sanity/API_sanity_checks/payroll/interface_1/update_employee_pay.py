import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class UpdateEmployeePay(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ep_id = payload.get("employee_pay_id") or payload.get("id")
        updates = payload.get("updates") or payload.get("data")
        if not ep_id or not isinstance(updates, dict):
            return {"success": False, "error": "missing_id_or_updates"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            eps = db.setdefault("employee_pays", [])
            for ep in eps:
                if ep.get("employee_pay_id") == ep_id:
                    ep.update(updates)
                    ep["updated_at"] = ts
                    db.setdefault("audit_log", []).append({"audit_id": f"audit_{ep_id}", "entity_type": "employee_pay", "entity_id": ep_id, "action_performed": "updated", "timestamp": ts})
                    return {"success": True, "employee_pay": ep}
            return {"success": False, "error": "not_found"}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "employee_pays.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            eps = raw
        elif isinstance(raw, dict):
            eps = list(raw.values())
        else:
            return {"success": False, "error": "bad_data"}

        for ep in eps:
            if ep.get("employee_pay_id") == ep_id:
                ep.update(updates)
                ep["updated_at"] = ts
                try:
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(eps, f, indent=2)
                    os.replace(tmp, path)
                except Exception as e:
                    return {"success": False, "error": "write_error", "details": str(e)}

                audit_entry = {"audit_id": f"audit_{ep_id}", "entity_type": "employee_pay", "entity_id": ep_id, "action_performed": "updated", "timestamp": ts}
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

                return {"success": True, "employee_pay": ep, "audit_entry": audit_entry}

        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], employee_pay_id: str, updates: Dict[str, Any]) -> str:
        try:
            res = UpdateEmployeePay._invoke_internal({"employee_pay_id": employee_pay_id, "updates": updates}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "update_employee_pay", "description": "Update an employee pay record.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "employee_pay_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["data", "employee_pay_id", "updates"]}}}
