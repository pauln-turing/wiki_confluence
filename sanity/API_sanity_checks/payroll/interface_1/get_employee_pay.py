import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetEmployeePay(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pay_id = payload.get("pay_id")
        if not pay_id:
            return {"success": False, "error": "missing_pay_id"}

        if db is not None:
            pays = db.get("employee_pays", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "employee_pays.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                pays = raw
            elif isinstance(raw, dict):
                pays = list(raw.values())
            else:
                pays = []

        for p in pays:
            if p.get("pay_id") == pay_id:
                return {"success": True, "pay": p}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], pay_id: str) -> str:
        try:
            res = GetEmployeePay._invoke_internal({"pay_id": pay_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_employee_pay", "description": "Retrieve an employee pay record by pay_id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "pay_id": {"type": "string"}}, "required": ["data", "pay_id"]}}}
