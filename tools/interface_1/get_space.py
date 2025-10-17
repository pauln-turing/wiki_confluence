
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetSpace(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Retrieves a space record by its key or ID.
        Args:
            payload (Dict[str, Any]): A dictionary containing the following keys:
                - space_key (str, optional): The key of the space to retrieve.
                - space_id (str, optional): The ID of the space to retrieve.
        Returns:
            Dict[str, Any]: A dictionary representing the space record, or an error message if not found.
        """
        space_key = payload.get("space_key")
        space_id = payload.get("space_id")

        if not space_key and not space_id:
            return json.dumps({"error": "Either 'space_key' or 'space_id' must be provided in the payload."})

        data_manager = DataManager()
        try:
            if space_id:
                space = data_manager.get_record("spaces", space_id)
            else:
                space = data_manager.find_by_field("spaces", "space_key", space_key)

            if space:
                return json.dumps(space)
            else:
                return json.dumps({"error": "Space not found."})
        except Exception as e:
            return json.dumps({"error": str(e)})
        
    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_space",
            "category": "Space Management",
            "description": "Retrieves a space record by its key or ID.",
            "arguments": "table_name='spaces', action='get', payload={space_key: str, space_id: str}",
            "flag": "Getter"
        }

