import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class CreateInvoice(Tool):
    @staticmethod
    def _generate_id(invoices: list[dict]) -> str:
        max_n = 0
        for inv in invoices:
            iid = inv.get("invoice_id", "")
            if isinstance(iid, str) and iid.startswith("inv_"):
                try:
                    n = int(iid.split("inv_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
        return f"inv_{(max_n + 1):03d}"

    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        invoice = payload.get("data_record") or payload.get("invoice")
        if not isinstance(invoice, dict):
            return {"success": False, "error": "invalid_input"}

        required = ["vendor_id", "amount"]
        missing = [k for k in required if not invoice.get(k)]
        if missing:
            return {"success": False, "error": "missing_fields", "missing": missing}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            invoices = db.setdefault("invoices", [])
            inv_id = CreateInvoice._generate_id(invoices)
            new_inv = {"invoice_id": inv_id, "vendor_id": invoice.get("vendor_id"), "amount": invoice.get("amount"), "status": "open", "created_at": ts}
            invoices.append(new_inv)
            db.setdefault("audit_log", []).append({"audit_id": f"audit_{inv_id}", "entity_type": "invoice", "entity_id": inv_id, "action_performed": "created", "timestamp": ts})
            return {"success": True, "invoice": new_inv}

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
            invoices = raw
        elif isinstance(raw, dict):
            invoices = list(raw.values())
        else:
            invoices = []

        inv_id = CreateInvoice._generate_id(invoices)
        new_inv = {"invoice_id": inv_id, "vendor_id": invoice.get("vendor_id"), "amount": invoice.get("amount"), "status": "open", "created_at": ts}

        try:
            invoices.append(new_inv)
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(invoices, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {"audit_id": f"audit_{inv_id}", "entity_type": "invoice", "entity_id": inv_id, "action_performed": "created", "timestamp": ts}
        try:
            audit_path = os.path.join(data_dir, "audit_log.json")
            if os.path.exists(audit_path):
                with open(audit_path, "r", encoding="utf-8") as f:
                    raw_a = json.load(f)
            else:
                raw_a = []
            if isinstance(raw_a, list):
                audit = raw_a
            elif isinstance(raw_a, dict):
                audit = list(raw_a.values())
            else:
                audit = []
            audit.append(audit_entry)
            tmpa = audit_path + ".tmp"
            with open(tmpa, "w", encoding="utf-8") as f:
                json.dump(audit, f, indent=2)
            os.replace(tmpa, audit_path)
        except Exception:
            pass

        return {"success": True, "invoice": new_inv, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], invoice_record: Dict[str, Any]) -> str:
        try:
            res = CreateInvoice._invoke_internal({"data_record": invoice_record}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_invoice",
                "description": "Create an invoice. Expects data dict and invoice record.",
                "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "invoice_record": {"type": "dict"}}, "required": ["data", "invoice_record"]}
            }
        }
