import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetEmployee(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        employee_id = payload.get("employee_id")
        if not employee_id:
            return {"success": False, "error": "missing_employee_id"}

        if db is not None:
            employees = db.get("employees", [])
        else:
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

        for e in employees:
            if e.get("employee_id") == employee_id:
                return {"success": True, "employee": e}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], employee_id: str) -> str:
        try:
            res = GetEmployee._invoke_internal({"employee_id": employee_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_employee",
                "description": "Retrieve an employee by employee_id. Expects data dict and employee_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "dict"},
                        "employee_id": {"type": "string"}
                    },
                    "required": ["data", "employee_id"]
                }
            }
        }
