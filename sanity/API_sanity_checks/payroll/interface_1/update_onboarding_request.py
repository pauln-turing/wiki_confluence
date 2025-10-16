import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class UpdateOnboardingRequest(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req_id = payload.get("onboarding_id") or payload.get("id")
        updates = payload.get("updates") or payload.get("data")
        if not req_id or not isinstance(updates, dict):
            return {"success": False, "error": "missing_id_or_updates"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            reqs = db.setdefault("onboarding_requests", [])
            for r in reqs:
                if r.get("onboarding_id") == req_id:
                    r.update(updates)
                    r["updated_at"] = ts
                    db.setdefault("audit_log", []).append({"audit_id": f"audit_{req_id}", "entity_type": "onboarding_request", "entity_id": req_id, "action_performed": "updated", "timestamp": ts})
                    return {"success": True, "onboarding_request": r}
            return {"success": False, "error": "not_found"}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "onboarding_requests.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            reqs = raw
        elif isinstance(raw, dict):
            reqs = list(raw.values())
        else:
            return {"success": False, "error": "bad_data"}

        for r in reqs:
            if r.get("onboarding_id") == req_id:
                r.update(updates)
                r["updated_at"] = ts
                try:
                    tmp = path + ".tmp"
                    with open(tmp, "w", encoding="utf-8") as f:
                        json.dump(reqs, f, indent=2)
                    os.replace(tmp, path)
                except Exception as e:
                    return {"success": False, "error": "write_error", "details": str(e)}

                audit_entry = {"audit_id": f"audit_{req_id}", "entity_type": "onboarding_request", "entity_id": req_id, "action_performed": "updated", "timestamp": ts}
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

                return {"success": True, "onboarding_request": r, "audit_entry": audit_entry}

        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], onboarding_id: str, updates: Dict[str, Any]) -> str:
        try:
            res = UpdateOnboardingRequest._invoke_internal({"onboarding_id": onboarding_id, "updates": updates}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "update_onboarding_request", "description": "Update an onboarding request.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "onboarding_id": {"type": "string"}, "updates": {"type": "object"}}, "required": ["data", "onboarding_id", "updates"]}}}
