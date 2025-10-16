
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import copy


class ClonePage(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        """
        Duplicates a page or an entire page tree.

        Args:
            payload: Dictionary containing:
                - source_page_id: str (required)
                - target_space_id: str (required)
                - target_parent_page_id: str (optional)
                - include_children: bool (default: False)
                - created_by_user_id: str (required)
                - new_title: str (optional, defaults to "Copy of [original title]")

        Returns:
            The cloned page record with metadata
        """
        source_page_id = payload.get("source_page_id")
        target_space_id = payload.get("target_space_id")
        created_by_user_id = payload.get("created_by_user_id")
        include_children = payload.get("include_children", False)

        if not source_page_id or not target_space_id or not created_by_user_id:
            raise ValueError(
                "source_page_id, target_space_id, and created_by_user_id are required")

        # Get source page
        source_page = DataManager.get_record("pages", source_page_id)
        if not source_page:
            raise ValueError(f"Source page {source_page_id} not found")

        # Verify target space exists
        if not DataManager.get_record("spaces", target_space_id):
            raise ValueError(f"Target space {target_space_id} not found")

        # Verify user exists
        if not DataManager.get_record("users", created_by_user_id):
            raise ValueError(f"User {created_by_user_id} not found")

        # Clone the page
        new_page_id = DataManager.get_next_id("pages")
        new_title = payload.get(
            "new_title") or f"Copy of {source_page.get('title', '')}"

        cloned_page_data = {
            "page_id": new_page_id,
            "space_id": target_space_id,
            "parent_page_id": payload.get("target_parent_page_id"),
            "title": new_title,
            "content_format": source_page.get("content_format", "markdown"),
            "current_version": 1,
            "state": "draft",
            "created_by_user_id": created_by_user_id,
            "updated_by_user_id": None,
            "created_at": DataManager.get_timestamp(),
            "updated_at": None,
            "is_trashed": False,
            "is_published": False
        }

        cloned_page = DataManager.create_record(
            "pages", new_page_id, cloned_page_data)

        # Clone the latest version content
        source_versions = DataManager.find_all_by_field(
            "page_versions", "page_id", source_page_id)
        if source_versions:
            # Get the latest version
            latest_version = max(
                source_versions, key=lambda v: v.get("version_number", 0))

            version_data = {
                "version_id": DataManager.get_next_id("page_versions"),
                "page_id": new_page_id,
                "version_number": 1,
                "editor_user_id": created_by_user_id,
                "edited_at": cloned_page_data["created_at"],
                "content_snapshot": latest_version.get("content_snapshot", "")
            }
            DataManager.create_record(
                "page_versions", version_data["version_id"], version_data)

        # Count children cloned
        children_cloned = 0
        if include_children:
            # Find all child pages
            all_pages = DataManager.get_all_records("pages")
            child_pages = [p for p_id, p in all_pages.items() if p.get(
                "parent_page_id") == source_page_id]

            for child_page in child_pages:
                # Recursively clone children
                child_payload = {
                    "source_page_id": child_page.get("page_id"),
                    "target_space_id": target_space_id,
                    "target_parent_page_id": new_page_id,
                    "include_children": True,
                    "created_by_user_id": created_by_user_id,
                    "new_title": child_page.get("title")
                }
                ClonePage.invoke(child_payload)
                children_cloned += 1

        # Add clone metadata
        cloned_page["source_page_id"] = source_page_id
        cloned_page["children_cloned"] = children_cloned

        return cloned_page

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "clone_page",
            "category": "Page Management",
            "description": "Duplicates a page or an entire page tree.",
            "arguments": "table_name='pages', action='clone', payload={source_page_id: str, target_space_id: str, target_parent_page_id: str, include_children: bool,created_by_user_id:str,\nnew_title:str}",
            "flag": "Setter"
        }
