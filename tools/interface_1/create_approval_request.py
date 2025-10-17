
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class CreateApprovalRequest(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Create an approval request.
        Args:
            payload (Dict[str, Any]): A dictionary containing the following keys:
                - target_entity_type (str): The type of entity for which the approval is requested (e.g., 'page', 'space').
                - target_entity_id (str): The ID of the target entity.
                - requested_by_user_id (str): The ID of the user requesting the approval.
                - reason (str, optional): The reason for the approval request.
                - due_at (str, optional): The due date for the approval in ISO 8601 format.
                - metadata (dict, optional): Additional metadata related to the approval request.
                - steps (list, optional): A list of steps involved in the approval process.
        Returns:
            Dict[str, Any]: A dictionary representing the created approval request, or an error message if creation fails.
        """
        required_fields = ["target_entity_type", "target_entity_id", "requested_by_user_id", "reason", "due_at", "metadata", "steps"]
        missing_fields = [field for field in required_fields if field not in payload]

        if missing_fields:
            return json.dumps({"error": f"Missing required fields: {', '.join(missing_fields)}"})
        
        # Check if entity type is valid and if the target entity exists
        data_manager = DataManager()
        try:
            entity = data_manager.get_record(f"{payload['target_entity_type']}", payload['target_entity_id'])
            if not entity:
                return json.dumps({"error": f"{payload['target_entity_type'].capitalize()} with ID {payload['target_entity_id']} not found."})
        except Exception as e:
            return json.dumps({"error": str(e)})

        
        try:
            new_id = data_manager.get_next_id("approval_requests")
            new_request = data_manager.create_record("approval_requests", new_id, payload)
            return json.dumps(new_request)
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "create_approval_request",
            "category": "Approval Management",
            "description": "Create an approval request",
            "arguments": "table_name='approval_requests', action='create', payload={target_entity_type: str, target_entity_id: str, requested_by_user_id: str, reason?: str, due_at?: datetime, metadata?: json, steps?: list}",
            "flag": "Setter"
        }

