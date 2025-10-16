import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class GenerateEmployeePays(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payroll_run_id = payload.get("payroll_run_id") or payload.get("run_id")
        if not payroll_run_id:
            return {"success": False, "error": "missing_payroll_run_id"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        def _create_pays(employees, run_id):
            pays = []
            counter = 1
            for e in employees:
                pays.append({"employee_pay_id": f"ep_{run_id}_{counter:03d}", "employee_id": e.get("employee_id"), "payroll_run_id": run_id, "amount": e.get("salary", 0), "created_at": ts})
                counter += 1
            return pays

        if db is not None:
            employees = db.get("employees", [])
            new_pays = _create_pays(employees, payroll_run_id)
            eps = db.setdefault("employee_pays", [])
            eps.extend(new_pays)
            db.setdefault("audit_log", []).append({"audit_id": f"audit_{payroll_run_id}", "entity_type": "payroll_run", "entity_id": payroll_run_id, "action_performed": "generated_employee_pays", "timestamp": ts})
            return {"success": True, "generated_count": len(new_pays), "employee_pays": new_pays}

        # file-backed
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")

        emps_path = os.path.join(data_dir, "employees.json")
        eps_path = os.path.join(data_dir, "employee_pays.json")

        try:
            with open(emps_path, "r", encoding="utf-8") as f:
                raw_emps = json.load(f)
        except Exception as e:
            return {"success": False, "error": "read_employees_error", "details": str(e)}

        if isinstance(raw_emps, list):
            employees = raw_emps
        elif isinstance(raw_emps, dict):
            employees = list(raw_emps.values())
        else:
            employees = []

        new_pays = _create_pays(employees, payroll_run_id)

        try:
            if os.path.exists(eps_path):
                with open(eps_path, "r", encoding="utf-8") as f:
                    raw_eps = json.load(f)
            else:
                raw_eps = []
        except Exception as e:
            raw_eps = []

        if isinstance(raw_eps, list):
            eps = raw_eps
        elif isinstance(raw_eps, dict):
            eps = list(raw_eps.values())
        else:
            eps = []

        eps.extend(new_pays)
        try:
            tmp = eps_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(eps, f, indent=2)
            os.replace(tmp, eps_path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {"audit_id": f"audit_{payroll_run_id}", "entity_type": "payroll_run", "entity_id": payroll_run_id, "action_performed": "generated_employee_pays", "timestamp": ts}
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

        return {"success": True, "generated_count": len(new_pays), "employee_pays": new_pays, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], run_id: str) -> str:
        try:
            res = GenerateEmployeePays._invoke_internal({"payroll_run_id": run_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "generate_employee_pays", "description": "Generate employee pays for a payroll run.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "run_id": {"type": "string"}}, "required": ["data", "run_id"]}}}
