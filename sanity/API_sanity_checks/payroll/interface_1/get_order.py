import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetOrder(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        order_id = payload.get("order_id")
        if not order_id:
            return {"success": False, "error": "missing_order_id"}

        if db is not None:
            orders = db.get("orders", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "orders.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                orders = raw
            elif isinstance(raw, dict):
                orders = list(raw.values())
            else:
                orders = []

        for o in orders:
            if o.get("order_id") == order_id:
                return {"success": True, "order": o}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], order_id: str) -> str:
        try:
            res = GetOrder._invoke_internal({"order_id": order_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_order", "description": "Retrieve an order by order_id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "order_id": {"type": "string"}}, "required": ["data", "order_id"]}}}
