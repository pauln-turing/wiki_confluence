import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetOffboardingRequest(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req_id = payload.get("request_id")
        if not req_id:
            return {"success": False, "error": "missing_request_id"}

        if db is not None:
            reqs = db.get("offboarding_requests", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "offboarding_requests.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                reqs = raw
            elif isinstance(raw, dict):
                reqs = list(raw.values())
            else:
                reqs = []

        for r in reqs:
            if r.get("request_id") == req_id:
                return {"success": True, "offboarding_request": r}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], request_id: str) -> str:
        try:
            res = GetOffboardingRequest._invoke_internal({"request_id": request_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_offboarding_request", "description": "Retrieve an offboarding request by request_id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "request_id": {"type": "string"}}, "required": ["data", "request_id"]}}}
