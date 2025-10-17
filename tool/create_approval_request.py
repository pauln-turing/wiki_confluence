
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class CreateApprovalRequest(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        try:
            # flat payload: target_entity_type, target_entity_id, requested_by_user_id, reason (opt), due_at (opt), metadata (opt), steps (opt list)
            target_entity_type = payload.get("target_entity_type")
            target_entity_id = payload.get("target_entity_id")
            requested_by_user_id = payload.get("requested_by_user_id")
            reason = payload.get("reason")
            due_at = payload.get("due_at")
            metadata = payload.get("metadata")

            rid = DataManager.get_next_id("approval_requests")
            req = {
                "target_entity_type": target_entity_type,
                "target_entity_id": target_entity_id,
                "requested_by_user_id": requested_by_user_id,
                "reason": reason,
                "due_at": due_at,
                "metadata": metadata,
                "status": "pending",
                "created_at": DataManager.get_timestamp(),
            }
            DataManager.create_record("approval_requests", rid, req)

            # create steps if provided as top-level 'steps'
            steps = payload.get("steps", [])
            created_steps = []
            for s in steps:
                sid = DataManager.get_next_id("approval_steps")
                s.setdefault("approval_request_id", rid)
                s.setdefault("status", "pending")
                DataManager.create_record("approval_steps", sid, s)
                created_steps.append({"step_id": sid, **s})

            return json.dumps({"request_id": rid, **req, "steps": created_steps})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "create_approval_request",
            "category": "Approval Management",
            "description": "Create an approval request",
            "arguments": "table_name=\'approval_requests\', action=\'create\', payload={target_entity_type: str, target_entity_id: str, requested_by_user_id: str, reason?: str, due_at?: datetime, metadata?: json, steps?: list}",
            "flag": "Setter"
        }

