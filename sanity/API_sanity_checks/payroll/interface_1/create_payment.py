import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class CreatePayment(Tool):
    @staticmethod
    def _generate_id(payments: list[dict]) -> str:
        max_n = 0
        for p in payments:
            pid = p.get("payment_id", "")
            if isinstance(pid, str) and pid.startswith("pay_"):
                try:
                    n = int(pid.split("pay_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
        return f"pay_{(max_n + 1):03d}"

    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payment = payload.get("data_record") or payload.get("payment")
        if not isinstance(payment, dict):
            return {"success": False, "error": "invalid_input"}

        required = ["amount", "method"]
        missing = [k for k in required if not payment.get(k)]
        if missing:
            return {"success": False, "error": "missing_fields", "missing": missing}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            payments = db.setdefault("payments", [])
            pid = CreatePayment._generate_id(payments)
            new_p = {"payment_id": pid, "amount": payment.get("amount"), "method": payment.get("method"), "status": "created", "created_at": ts}
            payments.append(new_p)
            db.setdefault("audit_log", []).append({"audit_id": f"audit_{pid}", "entity_type": "payment", "entity_id": pid, "action_performed": "created", "timestamp": ts})
            return {"success": True, "payment": new_p}

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

        pid = CreatePayment._generate_id(payments)
        new_p = {"payment_id": pid, "amount": payment.get("amount"), "method": payment.get("method"), "status": "created", "created_at": ts}

        try:
            payments.append(new_p)
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(payments, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {"audit_id": f"audit_{pid}", "entity_type": "payment", "entity_id": pid, "action_performed": "created", "timestamp": ts}
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

        return {"success": True, "payment": new_p, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], payment_record: Dict[str, Any]) -> str:
        try:
            res = CreatePayment._invoke_internal({"data_record": payment_record}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {"type": "function", "function": {"name": "create_payment", "description": "Create a payment.", "parameters": {"type": "object", "properties": {"data": {"type": "dict"}, "payment_record": {"type": "dict"}}, "required": ["data", "payment_record"]}}}
