import json
import os
from typing import Any, Dict, Optional
from base import Tool


class GetPendingApprovals:
    @staticmethod
    def invoke(data: Dict[str, Any], approver_id: str) -> str:
        """
        Retrieves a list of all approval requests that are still pending.
        """
        approvals = data.get("approvals", {})
        pending_requests = []
        for approval_id, record in approvals.items():
            if record.get("approver_id") == approver_id and record.get("decision") is None:
                pending_requests.append(record)
        
        return json.dumps({"success": True, "pending_approvals": pending_requests})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_pending_approvals",
                "description": "Retrieves a list of all approval requests that are still pending (i.e., decision is null) for a specific approver. Used by approvers to see their queue of items to review.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "dict",
                            "description": "The entire database of approvals."
                        },
                        "approver_id": {
                            "type": "string",
                            "description": "The ID of the approver whose pending requests are to be retrieved."
                        }
                    },
                    "required": ["data", "approver_id"]
                }
            }
        }