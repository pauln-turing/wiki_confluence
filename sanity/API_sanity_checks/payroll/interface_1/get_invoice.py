import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetInvoice(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        invoice_id = payload.get("invoice_id")
        if not invoice_id:
            return {"success": False, "error": "missing_invoice_id"}

        if db is not None:
            invs = db.get("invoices", [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, "invoices.json")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                invs = raw
            elif isinstance(raw, dict):
                invs = list(raw.values())
            else:
                invs = []

        for i in invs:
            if i.get("invoice_id") == invoice_id:
                return {"success": True, "invoice": i}
        return {"success": False, "error": "not_found"}

    @staticmethod
    def invoke(data: Dict[str, Any], invoice_id: str) -> str:
        try:
            res = GetInvoice._invoke_internal({"invoice_id": invoice_id}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "get_invoice", "description": "Retrieve an invoice by invoice_id.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "invoice_id": {"type": "string"}}, "required": ["data", "invoice_id"]}}}
