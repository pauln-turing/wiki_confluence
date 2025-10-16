import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetPayrollRun(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payroll_run_id = payload.get("payroll_run_id")
        if not payroll_run_id:
            return {"success": False, "error": "missing_payroll_run_id"}

        if db is not None:
            runs = db.get("payroll_runs", [])
        else:
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

        for r in runs:
            if r.get("payroll_run_id") == payroll_run_id:
                return {"success": True, "payroll_run": r}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], payroll_run_id: str) -> str:
        try:
            res = GetPayrollRun._invoke_internal({"payroll_run_id": payroll_run_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_payroll_run", "description": "Retrieve a payroll run by id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "payroll_run_id": {"type": "string"}}, "required": ["data", "payroll_run_id"]}}}
