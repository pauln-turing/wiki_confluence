
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class DecideApprovalStep(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        try:
            step_id = payload.get("step_id")
            approver = payload.get("approver_user_id")
            decision = payload.get("decision")
            comment = payload.get("comment")

            if not step_id or not approver or not decision:
                return json.dumps({"error": "step_id, approver_user_id and decision are required"})

            # record decision
            did = DataManager.get_next_id("approval_decisions")
            dec = {"step_id": step_id, "approver_user_id": approver, "decision": decision, "comment": comment, "created_at": DataManager.get_timestamp()}
            DataManager.create_record("approval_decisions", did, dec)

            # update step status
            updated_step = DataManager.update_record("approval_steps", step_id, {"status": decision, "decided_at": DataManager.get_timestamp()})

            # check overall request status
            req_id = updated_step.get("approval_request_id")
            if req_id:
                steps = DataManager.find_all_by_field("approval_steps", "approval_request_id", req_id)
                statuses = [s.get("status") for s in steps]
                if all(s == "approved" for s in statuses):
                    DataManager.update_record("approval_requests", req_id, {"status": "approved", "updated_at": DataManager.get_timestamp()})
                elif any(s == "rejected" for s in statuses):
                    DataManager.update_record("approval_requests", req_id, {"status": "rejected", "updated_at": DataManager.get_timestamp()})

            return json.dumps({"decision_id": did, **dec})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "decide_approval_step",
            "category": "Approval Management",
            "description": "Records a decision for an approval step and updates overall status.",
            "arguments": "table_name=\'approval_decisions\', action=\'update\', payload={step_id: str, approver_user_id: str, decision: decision_type, comment?: str}",
            "flag": "Setter"
        }

