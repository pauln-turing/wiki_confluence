import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetDepartment(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        department_id = payload.get("department_id")
        if not department_id:
            return {"success": False, "error": "missing_department_id"}

        if db is not None:
            depts = db.get("departments", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "departments.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                depts = raw
            elif isinstance(raw, dict):
                depts = list(raw.values())
            else:
                depts = []

        for d in depts:
            if d.get("department_id") == department_id:
                return {"success": True, "department": d}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], department_id: str) -> str:
        try:
            res = GetDepartment._invoke_internal({"department_id": department_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_department", "description": "Retrieve a department by department_id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "department_id": {"type": "string"}}, "required": ["data", "department_id"]}}}
