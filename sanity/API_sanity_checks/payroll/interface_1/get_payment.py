import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetPayment(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payment_id = payload.get("payment_id")
        if not payment_id:
            return {"success": False, "error": "missing_payment_id"}

        if db is not None:
            payments = db.get("payments", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "payments.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                payments = raw
            elif isinstance(raw, dict):
                payments = list(raw.values())
            else:
                payments = []

        for p in payments:
            if p.get("payment_id") == payment_id:
                return {"success": True, "payment": p}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], payment_id: str) -> str:
        try:
            res = GetPayment._invoke_internal({"payment_id": payment_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_payment", "description": "Retrieve a payment by payment_id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "payment_id": {"type": "string"}}, "required": ["data", "payment_id"]}}}
