import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class CreateDispute(Tool):
    @staticmethod
    def _generate_id(disputes: list[dict]) -> str:
        max_n = 0
        for d in disputes:
            did = d.get("dispute_id", "")
            if isinstance(did, str) and did.startswith("disp_"):
                try:
                    n = int(did.split("disp_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
        return f"disp_{(max_n + 1):03d}"

    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data_rec = payload.get("data_record") or payload.get("dispute")
        if not isinstance(data_rec, dict):
            return {"success": False, "error": "invalid_input"}

        required = ["dispute_type", "entity_id", "description"]
        missing = [k for k in required if not data_rec.get(k)]
        if missing:
            return {"success": False, "error": "missing_fields", "missing": missing}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            disputes = db.setdefault("disputes", [])
            disp_id = CreateDispute._generate_id(disputes)
            new_d = {"dispute_id": disp_id, "dispute_type": data_rec.get("dispute_type"), "entity_id": data_rec.get("entity_id"), "description": data_rec.get("description"), "status": "open", "created_at": ts}
            disputes.append(new_d)
            db.setdefault("audit_log", []).append({"audit_id": f"audit_{disp_id}", "entity_type": "dispute", "entity_id": disp_id, "action_performed": "created", "timestamp": ts})
            return {"success": True, "dispute": new_d}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "disputes.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            else:
                raw = []
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            disputes = raw
        elif isinstance(raw, dict):
            disputes = list(raw.values())
        else:
            disputes = []

        disp_id = CreateDispute._generate_id(disputes)
        new_d = {"dispute_id": disp_id, "dispute_type": data_rec.get("dispute_type"), "entity_id": data_rec.get("entity_id"), "description": data_rec.get("description"), "status": "open", "created_at": ts}

        try:
            disputes.append(new_d)
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(disputes, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {"audit_id": f"audit_{disp_id}", "entity_type": "dispute", "entity_id": disp_id, "action_performed": "created", "timestamp": ts}
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

        return {"success": True, "dispute": new_d, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], dispute_record: Dict[str, Any]) -> str:
        try:
            res = CreateDispute._invoke_internal({"data_record": dispute_record}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_dispute",
                "description": "Create a dispute record. Expects data dict and dispute record.",
                "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "dispute_record": {"type": "dict"}}, "required": ["data", "dispute_record"]}
            }
        }
