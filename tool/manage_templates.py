
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageTemplates(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "create":
                # flat payload: template_name, template_content, is_blueprint, space_id
                template_name = payload.get("template_name")
                template_content = payload.get("template_content")
                is_blueprint = payload.get("is_blueprint")
                space_id = payload.get("space_id")
                template = {"name": template_name, "content": template_content, "is_blueprint": is_blueprint, "space_id": space_id}
                template_id = DataManager.get_next_id("templates")
                DataManager.create_record("templates", template_id, template)
                return json.dumps({"template_id": template_id, **template})

            if action == "update":
                template_id = payload.get("template_id")
                if not template_id:
                    return json.dumps({"error": "'template_id' is required for update"})
                updates = {}
                if "template_name" in payload:
                    updates["name"] = payload.get("template_name")
                if "template_content" in payload:
                    updates["content"] = payload.get("template_content")
                if "is_blueprint" in payload:
                    updates["is_blueprint"] = payload.get("is_blueprint")
                if not updates:
                    updates = payload.get("updates", {})
                updated = DataManager.update_record("templates", str(template_id), updates)
                return json.dumps(updated)

            if action == "delete":
                template_id = payload.get("template_id")
                if not template_id:
                    return json.dumps({"error": "'template_id' is required for delete"})
                DataManager.delete_record("templates", str(template_id))
                return json.dumps({"deleted": True, "template_id": template_id})

            return json.dumps({"error": "Unsupported or missing action. Use create/update/delete."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_templates",
            "category": "Template Management",
            "description": "Creates, updates, or deletes a template.",
            "arguments": "table_name=\'templates\', action=\'create/update/delete\', payload={template_id: str, template_name: str, template_content: str, is_blueprint: bool, space_id: str}",
            "flag": "Setter"
        }

