
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class UseTemplate(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        template_id = payload.get("template_id")
        # flat payload target fields: title, space_id
        title = payload.get("title")
        space_id = payload.get("space_id")
        try:
            if not template_id:
                return json.dumps({"error": "'template_id' is required"})
            template = DataManager.get_record("templates", str(template_id))
            if not template:
                return json.dumps({"error": "Template not found"})
            # create a page from template
            page_id = DataManager.get_next_id("pages")
            page = {"title": title or template.get("name"), "content": template.get("content"), "space_id": space_id, "created_at": DataManager.get_timestamp()}
            DataManager.create_record("pages", page_id, page)
            return json.dumps({"page_id": page_id, **page})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "use_template",
            "category": "Template Management",
            "description": "Creates a new space or page using a template.",
            "arguments": "table_name='templates', action='use', payload={template_id: str, space_id: str, page_title: str}",
            "flag": "Setter"
        }

