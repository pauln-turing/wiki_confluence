import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class UpdateEmployee(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        emp_id = payload.get("employee_id") or payload.get("id")
        updates = payload.get("updates") or payload.get("data")
        if not emp_id or not isinstance(updates, dict):
            return {"success": False, "error": "missing_id_or_updates"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            emps = db.setdefault("employees", [])
            for e in emps:
                if e.get("employee_id") == emp_id:
                    e.update(updates)
                    e["updated_at"] = ts
                    db.setdefault("audit_log", []).append({"audit_id": f"audit_{emp_id}", "entity_type": "employee", "entity_id": emp_id, "action_performed": "updated", "timestamp": ts})
                    return {"success": True, "employee": e}
            return {"success": False, "error": "not_found"}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "employees.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            emps = raw
        elif isinstance(raw, dict):
            emps = list(raw.values())
        else:
            return {"success": False, "error": "bad_data"}

        for e in emps:
            if e.get("employee_id") == emp_id:
                e.update(updates)
                e["updated_at"] = ts
                try:
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(emps, f, indent=2)
                    os.replace(tmp, path)
                except Exception as e:
                    return {"success": False, "error": "write_error", "details": str(e)}

                audit_entry = {"audit_id": f"audit_{emp_id}", "entity_type": "employee", "entity_id": emp_id, "action_performed": "updated", "timestamp": ts}
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

                return {"success": True, "employee": e, "audit_entry": audit_entry}

        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: str, updates: Dict[str, Any]) -> str:
        try:
            res = UpdateEmployee._invoke_internal({"employee_id": employee_id, "updates": updates}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "update_employee", "description": "Update an employee record.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "employee_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["data", "employee_id", "updates"]}}}
