import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class CreatePayrollRun(Tool):
    @staticmethod
    def _generate_id(runs: list[dict]) -> str:
        max_n = 0
        for r in runs:
            rid = r.get("payroll_run_id", "")
            if isinstance(rid, str) and rid.startswith("pr_"):
                try:
                    n = int(rid.split("pr_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
        return f"pr_{(max_n + 1):03d}"

    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data_rec = payload.get("data_record") or payload.get("payroll_run")
        if not isinstance(data_rec, dict):
            return {"success": False, "error": "invalid_input"}

        required = ["payroll_period_start", "payroll_period_end", "gross_total"]
        missing = [k for k in required if not data_rec.get(k)]
        if missing:
            return {"success": False, "error": "missing_fields", "missing": missing}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        if db is not None:
            runs = db.setdefault("payroll_runs", [])
            run_id = CreatePayrollRun._generate_id(runs)
            new_run = {"payroll_run_id": run_id, "payroll_period_start": data_rec.get("payroll_period_start"), "payroll_period_end": data_rec.get("payroll_period_end"), "gross_total": data_rec.get("gross_total"), "created_at": ts}
            runs.append(new_run)
            db.setdefault("audit_log", []).append({"audit_id": f"audit_{run_id}", "entity_type": "payroll_run", "entity_id": run_id, "action_performed": "created", "timestamp": ts})
            return {"success": True, "payroll_run": new_run}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "payroll_runs.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            else:
                raw = []
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            runs = raw
        elif isinstance(raw, dict):
            runs = list(raw.values())
        else:
            runs = []

        run_id = CreatePayrollRun._generate_id(runs)
        new_run = {"payroll_run_id": run_id, "payroll_period_start": data_rec.get("payroll_period_start"), "payroll_period_end": data_rec.get("payroll_period_end"), "gross_total": data_rec.get("gross_total"), "created_at": ts}

        try:
            runs.append(new_run)
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(runs, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {"audit_id": f"audit_{run_id}", "entity_type": "payroll_run", "entity_id": run_id, "action_performed": "created", "timestamp": ts}
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

        return {"success": True, "payroll_run": new_run, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], run_record: Dict[str, Any]) -> str:
        try:
            res = CreatePayrollRun._invoke_internal({"data_record": run_record}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "create_payroll_run", "description": "Create a payroll run.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "run_record": {"type": "dict"}}, "required": ["data", "run_record"]}}}
