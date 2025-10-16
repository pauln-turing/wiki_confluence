import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetDispute(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        dispute_id = payload.get("dispute_id")
        if not dispute_id:
            return {"success": False, "error": "missing_dispute_id"}

        if db is not None:
            disputes = db.get("disputes", [])
        else:
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

        for d in disputes:
            if d.get("dispute_id") == dispute_id:
                return {"success": True, "dispute": d}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], dispute_id: str) -> str:
        try:
            res = GetDispute._invoke_internal({"dispute_id": dispute_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_dispute", "description": "Retrieve a dispute by dispute_id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "dispute_id": {"type": "string"}}, "required": ["data", "dispute_id"]}}}
