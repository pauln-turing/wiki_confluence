
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageSpaceFeatures(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "set":
                feature = payload.get("feature", {})
                fid = DataManager.get_next_id("space_features")
                DataManager.create_record("space_features", fid, feature)
                return json.dumps({"feature_id": fid, **feature})

            if action == "update":
                feature_id = payload.get("feature_id")
                if not feature_id:
                    return json.dumps({"error": "'feature_id' is required for update"})
                updates = payload.get("updates", {})
                updated = DataManager.update_record("space_features", str(feature_id), updates)
                return json.dumps(updated)

            return json.dumps({"error": "Unsupported or missing action. Use set/update."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_space_features",
            "category": "Space Management",
            "description": "Manages which features are enabled for a space.",
            "arguments": "table_name='space_features', action='manage', payload={space_id: str, feature_type: space_feature_type, is_enabled: bool}",
            "flag": "Setter"
        }

