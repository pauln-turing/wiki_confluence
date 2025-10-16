
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
        query = "SELECT label FROM page_labels WHERE page_id = %s"
        results = data_manager.find_all_by_field("page_labels", "page_id", page_id)
        return json.dumps(results)
        
    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "get_labels",
            "category": "Content Management",
            "description": "Retrieves all labels for a page.",
            "arguments": "table_name=\'page_labels\', action=\'get\', payload={page_id: str}",
            "flag": "Getter"
        }

