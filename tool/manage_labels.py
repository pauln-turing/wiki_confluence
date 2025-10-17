
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageLabels(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "add":
                # flat payload: page_id, label_names (list)
                page_id = payload.get("page_id")
                labels = payload.get("label_names", [])
                created = []
                for name in labels:
                    rec = {"page_id": page_id, "label": name}
                    lid = DataManager.get_next_id("page_labels")
                    DataManager.create_record("page_labels", lid, rec)
                    created.append({"label_id": lid, **rec})
                return json.dumps(created)

            if action == "remove":
                label_id = payload.get("label_id")
                if not label_id:
                    return json.dumps({"error": "'label_id' is required for remove"})
                DataManager.delete_record("page_labels", str(label_id))
                return json.dumps({"deleted": True, "label_id": label_id})

            return json.dumps({"error": "Unsupported or missing action. Use add/remove."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_labels",
            "category": "Content Management",
            "description": "Adds or removes labels from a page.",
            "arguments": "table_name=\'page_labels\', action=\'add/remove\', payload={page_id: str, label_names: list}",
            "flag": "Setter"
        }

