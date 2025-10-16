import json
import os
from typing import Any, Dict, Optional
from datetime import datetime, timezone
from base import Tool


class SubmitApprovalDecision:
    @staticmethod
    def invoke(data: Dict[str, Any], approval_id: str, decision: str, comments: Optional[str], performed_by: str) -> str:
        """
        Submits a decision for a pending approval request.
        """
        approvals = data.get("approvals", {})
        
        if approval_id not in approvals:
            return json.dumps({"success": False, "error": "Request Not Found"})
            
        allowed_decisions = ["approved", "rejected", "escalated"]
        if decision not in allowed_decisions:
            return json.dumps({"success": False, "error": "Invalid Decision"})
            
        record = approvals[approval_id]
        
        record["decision"] = decision
        record["comments"] = comments
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        return json.dumps({"success": True, "updated_record": record})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "submit_approval_decision",
                "description": "Submits a decision for a pending approval request. Used by an approver to approve, reject, or escalate an item. Updates the approval record with the decision and comments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "dict",
                            "description": "The entire database of approvals."
                        },
                        "approval_id": {
                            "type": "string",
                            "description": "The ID of the approval request to be updated."
                        },
                        "decision": {
                            "type": "string",
                            "description": "The decision to submit. Must be one of: 'approved', 'rejected', 'escalated'."
                        },
                        "comments": {
                            "type": "string",
                            "description": "Optional comments for the decision."
                        },
                        "performed_by": {
                            "type": "string",
                            "description": "The ID of the user submitting the decision."
                        }
                    },
                    "required": ["data", "approval_id", "decision", "performed_by"]
                }
            }
        }