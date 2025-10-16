import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class CreateOffboardingRequest(Tool):
    @staticmethod
    def _generate_id(reqs: list[dict]) -> str:
        max_n = 0
        for r in reqs:
            rid = r.get("request_id", "")
            if isinstance(rid, str) and rid.startswith("off_"):
                try:
                    n = int(rid.split("off_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
        return f"off_{(max_n + 1):03d}"

    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data_rec = payload.get("data_record") or payload.get("request")
        if not isinstance(data_rec, dict):
            return {"success": False, "error": "invalid_input"}

        required = ["employee_id", "reason"]
        missing = [k for k in required if not data_rec.get(k)]
        if missing:
            return {"success": False, "error": "missing_fields", "missing": missing}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            reqs = db.setdefault("offboarding_requests", [])
            request_id = CreateOffboardingRequest._generate_id(reqs)
            new_r = {"request_id": request_id, "employee_id": data_rec.get("employee_id"), "reason": data_rec.get("reason"), "status": "requested", "created_at": ts}
            reqs.append(new_r)
            db.setdefault("audit_log", []).append({"audit_id": f"audit_{request_id}", "entity_type": "offboarding_request", "entity_id": request_id, "action_performed": "created", "timestamp": ts})
            return {"success": True, "request": new_r}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "offboarding_requests.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            else:
                raw = []
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            reqs = raw
        elif isinstance(raw, dict):
            reqs = list(raw.values())
        else:
            reqs = []

        request_id = CreateOffboardingRequest._generate_id(reqs)
        new_r = {"request_id": request_id, "employee_id": data_rec.get("employee_id"), "reason": data_rec.get("reason"), "status": "requested", "created_at": ts}

        try:
            reqs.append(new_r)
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(reqs, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {"audit_id": f"audit_{request_id}", "entity_type": "offboarding_request", "entity_id": request_id, "action_performed": "created", "timestamp": ts}
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

        return {"success": True, "request": new_r, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], request_record: Dict[str, Any]) -> str:
        try:
            res = CreateOffboardingRequest._invoke_internal({"data_record": request_record}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "create_offboarding_request", "description": "Create an offboarding request.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "request_record": {"type": "dict"}}, "required": ["data", "request_record"]}}}
