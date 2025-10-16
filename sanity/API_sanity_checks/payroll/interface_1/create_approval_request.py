import json
import os
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from base import Tool



class CreateApprovalRequest:
    @staticmethod
    def invoke(data: Dict[str, Any], data_record: Dict[str, Any]) -> str:
        """
        Creates a new approval request record.
        """
        approvals = data.get("approvals", {})
        
        required_fields = ["entity_type", "entity_id", "approver_id", "level"]
        if not all(field in data_record for field in required_fields):
            return json.dumps({"success": False, "error": "Invalid or Missing Inputs"})
            
        def generate_id(table: Dict[str, Any]) -> str:
            if not table:
                return "app_001"
            last_key = max(table.keys(), key=lambda k: int(k.split('_')[1]))
            last_number = int(last_key.split('_')[1])
            new_number = last_number + 1
            return f"app_{new_number:03d}"
            
        new_approval_id = generate_id(approvals)
        
        record_to_create = {
            "approval_id": new_approval_id,
            "decision": None,
            "comments": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        record_to_create.update(data_record)
        
        approvals[new_approval_id] = record_to_create
        
        return json.dumps({"success": True, "created_approval_request": record_to_create})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_approval_request",
                "description": "Creates a new approval request record for an entity (e.g., payroll run, invoice, order). This tool is used to initiate the approval workflow.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "dict",
                            "description": "The entire database of approvals."
                        },
                        "data_record": {
                            "type": "dict",
                            "description": "A dictionary containing the data for the new approval request. Must include 'entity_type', 'entity_id', 'approver_id', and 'level'."
                        }
                    },
                    "required": ["data", "data_record"]
                }
            }
        }
