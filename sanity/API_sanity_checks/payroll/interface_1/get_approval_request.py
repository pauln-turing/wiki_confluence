import json
from typing import Any, Dict
from base import Tool

class GetApprovalRequest(Tool):
    @staticmethod
    def invoke(data: Dict[str, Any], approval_id: str) -> str:
        """
        Retrieves a single approval request record by its unique ID.
        """
        approvals = data.get("approvals", {})
        approval_record = approvals.get(approval_id)
        if approval_record:
            return json.dumps({"success": True, "approval_request": approval_record})
        else:
            return json.dumps({"success": False, "error": f"Approval request with ID {approval_id} not found."})

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_approval_request",
                "description": "Retrieves a single approval request record by its unique ID. Essential for fetching details about a specific approval request for validation or display.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "dict",
                            "description": "The entire database of approvals."
                        },
                        "approval_id": {
                            "type": "string",
                            "description": "The unique ID of the approval request to retrieve."
                        }
                    },
                    "required": ["data", "approval_id"]
                }
            }
        }
