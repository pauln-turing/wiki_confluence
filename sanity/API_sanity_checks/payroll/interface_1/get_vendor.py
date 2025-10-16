import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetVendor(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        vendor_id = payload.get("vendor_id")
        if not vendor_id:
            return {"success": False, "error": "missing_vendor_id"}

        if db is not None:
            vendors = db.get("vendors", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "vendors.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                vendors = raw
            elif isinstance(raw, dict):
                vendors = list(raw.values())
            else:
                vendors = []

        for v in vendors:
            if v.get("vendor_id") == vendor_id:
                return {"success": True, "vendor": v}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], vendor_id: str) -> str:
        """
        Approvals-style wrapper: expects an in-memory `data` dict and a vendor_id string. Returns JSON string.
        """
        try:
            res = GetVendor._invoke_internal({"vendor_id": vendor_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_vendor",
                "description": "Retrieve a vendor by vendor_id. Expects an in-memory data dict and vendor_id.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "dict", "description": "In-memory database (tables as dicts)."},
                        "vendor_id": {"type": "string", "description": "The vendor_id to lookup."}
                    },
                    "required": ["data", "vendor_id"]
                }
            }
        }
