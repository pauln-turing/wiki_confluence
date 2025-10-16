import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class CreateEmployee(Tool):
    @staticmethod
    def _generate_employee_id(employees: list[dict]) -> str:
        max_n = 0
        for e in employees:
            eid = e.get("employee_id", "")
            if isinstance(eid, str) and eid.startswith("emp_"):
                try:
                    n = int(eid.split("emp_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
        return f"emp_{(max_n + 1):03d}"

    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # support multiple payload key names for compatibility: data_record, data, employee
        employee = payload.get("data_record") or payload.get("data") or payload.get("employee")
        if not isinstance(employee, dict):
            return {"success": False, "error": "invalid_input"}

        required = ["name", "role", "salary", "tax_id", "bank_account_number", "bank_routing_number", "department_id"]
        missing = [k for k in required if not employee.get(k) and employee.get(k) != 0]
        if missing:
            return {"success": False, "error": "missing_fields", "missing": missing}

        try:
            employee["salary"] = float(employee["salary"])
        except Exception:
            return {"success": False, "error": "invalid_field", "details": "salary must be numeric"}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            employees = db.setdefault("employees", [])
            for emp in employees:
                if emp.get("tax_id") == employee.get("tax_id"):
                    return {"success": False, "error": "duplicate_tax_id"}
            employee_id = CreateEmployee._generate_employee_id(employees)
            new_emp = {
                "employee_id": employee_id,
                "name": employee["name"],
                "role": employee["role"],
                "salary": employee["salary"],
                "tax_id": employee["tax_id"],
                "bank_account_number": employee["bank_account_number"],
                "bank_routing_number": employee["bank_routing_number"],
                "department_id": employee["department_id"],
                "created_at": ts,
                "updated_at": ts,
                "status": "active",
            }
            employees.append(new_emp)
            db.setdefault("audit_log", []).append({
                "audit_id": f"audit_{employee_id}",
                "entity_type": "employee",
                "entity_id": employee_id,
                "action_performed": "employee_created",
                "timestamp": ts,
                "user_role": "HR",
            })
            return {"success": True, "employee": new_emp}

        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        data_dir = os.path.join(workspace_root, "data")
        path = os.path.join(data_dir, "employees.json")

        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            else:
                raw = []
        except Exception as e:
            return {"success": False, "error": "read_error", "details": str(e)}

        if isinstance(raw, list):
            employees = raw
        elif isinstance(raw, dict):
            employees = list(raw.values())
        else:
            employees = []

        for emp in employees:
            if emp.get("tax_id") == employee.get("tax_id"):
                return {"success": False, "error": "duplicate_tax_id"}

        employee_id = CreateEmployee._generate_employee_id(employees)
        new_emp = {
            "employee_id": employee_id,
            "name": employee["name"],
            "role": employee["role"],
            "salary": employee["salary"],
            "tax_id": employee["tax_id"],
            "bank_account_number": employee["bank_account_number"],
            "bank_routing_number": employee["bank_routing_number"],
            "department_id": employee["department_id"],
            "created_at": ts,
            "updated_at": ts,
            "status": "active",
        }

        try:
            employees.append(new_emp)
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(employees, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {
            "audit_id": f"audit_{employee_id}",
            "entity_type": "employee",
            "entity_id": employee_id,
            "action_performed": "employee_created",
            "timestamp": ts,
            "user_role": "HR",
        }
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

        return {"success": True, "employee": new_emp, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], employee_record: Dict[str, Any]) -> str:
        try:
            res = CreateEmployee._invoke_internal({"data": employee_record}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_employee",
                "description": "Create a new employee record. Expects in-memory data dict and employee data record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "dict"},
                        "employee_record": {"type": "dict"}
                    },
                    "required": ["data", "employee_record"]
                }
            }
        }
