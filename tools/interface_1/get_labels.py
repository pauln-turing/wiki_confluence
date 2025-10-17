
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class GetLabels(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Retrieves all labels for a page.
        Args:
            payload (Dict[str, Any]): A dictionary containing the following keys:
                - page_id (str): The ID of the page to retrieve labels for.
        Returns:
            List[str]: A list of labels associated with the specified page.
        """
        page_id = payload.get("page_id")
        if not page_id:
            raise ValueError("The 'page_id' must be provided in the payload.")

        data_manager = DataManager()
        try:
            labels = data_manager.find_all_by_field("page_labels", "page_id", page_id)
            if labels:
                return json.dumps(labels)
            else:
                return json.dumps({"error": "No labels found for the specified page."})
        except Exception as e:
            return json.dumps({"error": str(e)})
        
    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_labels",
            "category": "Content Management",
            "description": "Retrieves all labels for a page.",
            "arguments": "table_name='page_labels', action='get', payload={page_id: str}",
            "flag": "Getter"
        }

