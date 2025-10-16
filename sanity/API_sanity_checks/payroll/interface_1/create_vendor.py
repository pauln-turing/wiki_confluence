import json
import os
from typing import Any, Dict, Optional
from datetime import datetime
from base import Tool


class CreateVendor(Tool):
    @staticmethod
    def _generate_vendor_id(vendors: list[dict]) -> str:
        max_n = 0
        for v in vendors:
            vid = v.get("vendor_id", "")
            if isinstance(vid, str) and vid.startswith("ven_"):
                try:
                    n = int(vid.split("ven_")[-1])
                    if n > max_n:
                        max_n = n
                except Exception:
                    continue
        return f"ven_{(max_n + 1):03d}"

    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # support multiple payload key names for compatibility: data_record, data, vendor
        vendor = payload.get("data_record") or payload.get("data") or payload.get("vendor")
        if not isinstance(vendor, dict):
            return {"success": False, "error": "invalid_input"}

        required = ["name", "tax_id", "bank_account_number", "bank_routing_number"]
        missing = [k for k in required if not vendor.get(k) and vendor.get(k) != 0]
        if missing:
            return {"success": False, "error": "missing_fields", "missing": missing}

        ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        if db is not None:
            vendors = db.setdefault("vendors", [])
            for v in vendors:
                if v.get("tax_id") == vendor.get("tax_id"):
                    return {"success": False, "error": "duplicate_tax_id"}
            vendor_id = CreateVendor._generate_vendor_id(vendors)
            new_v = {
                "vendor_id": vendor_id,
                "name": vendor.get("name"),
                "tax_id": vendor.get("tax_id"),
                "bank_account_number": vendor.get("bank_account_number"),
                "bank_routing_number": vendor.get("bank_routing_number"),
                "created_at": ts,
                "updated_at": ts,
            }
            vendors.append(new_v)
            db.setdefault("audit_log", []).append({
                "audit_id": f"audit_{vendor_id}",
                "entity_type": "vendor",
                "entity_id": vendor_id,
                "action_performed": "vendor_created",
                "timestamp": ts,
                "user_role": "Procurement",
            })
            return {"success": True, "vendor": new_v}

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
            if v.get("tax_id") == vendor.get("tax_id"):
                return {"success": False, "error": "duplicate_tax_id"}

        vendor_id = CreateVendor._generate_vendor_id(vendors)
        new_v = {
            "vendor_id": vendor_id,
            "name": vendor.get("name"),
            "tax_id": vendor.get("tax_id"),
            "bank_account_number": vendor.get("bank_account_number"),
            "bank_routing_number": vendor.get("bank_routing_number"),
            "created_at": ts,
            "updated_at": ts,
        }

        try:
            vendors.append(new_v)
            tmp = path + ".tmp"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(vendors, f, indent=2)
            os.replace(tmp, path)
        except Exception as e:
            return {"success": False, "error": "write_error", "details": str(e)}

        audit_entry = {
            "audit_id": f"audit_{vendor_id}",
            "entity_type": "vendor",
            "entity_id": vendor_id,
            "action_performed": "vendor_created",
            "timestamp": ts,
            "user_role": "Procurement",
        }
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

        return {"success": True, "vendor": new_v, "audit_entry": audit_entry}

    @staticmethod
    def invoke(data: Dict[str, Any], vendor_record: Dict[str, Any]) -> str:
        try:
            res = CreateVendor._invoke_internal({"data": vendor_record}, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_vendor",
                "description": "Create a new vendor record. Expects in-memory data dict and vendor data record.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "dict"},
                        "vendor_record": {"type": "dict"}
                    },
                    "required": ["data", "vendor_record"]
                }
            }
        }
