import json
from typing import Any, Dict, Optional
from tau_bench.envs.tool import Tool


class CreateSpace(Tool):
    """
    Creates a new space record in the in-memory JSON database (data dict).
    """

    @staticmethod
    def _generate_id(table: Dict[str, Any]) -> str:
        if not table:
            return "1"
        try:
            return str(max(int(k) for k in table.keys()) + 1)
        except ValueError:
            return str(len(table) + 1)

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        space_key: str,
        space_name: str,
        created_by_user_id: str,
        space_purpose: Optional[str] = None
    ) -> str:
        spaces = data.get("spaces", {})
        if not space_key or not space_name or not created_by_user_id:
            return json.dumps({"error": "Missing or invalid inputs (space_key, space_name, created_by_user_id)"} )

        for rec in spaces.values():
            if rec.get("space_key") == space_key:
                return json.dumps({"error": "space_key already exists"})

        space_id = CreateSpace._generate_id(spaces)
        timestamp = "2025-10-01T00:00:00"

        new_space = {
            "space_id": space_id,
            "space_key": space_key,
            "space_name": space_name,
            "space_purpose": space_purpose,
            "created_by_user_id": created_by_user_id,
            "created_at": timestamp,
            "is_deleted": False,
            "deleted_at": None,
            "updated_at": timestamp,
        }

        spaces[str(space_id)] = new_space
        data["spaces"] = spaces
        return json.dumps(new_space)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "create_space",
                "description": "Create a new space. Validates unique space_key and stores metadata.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "space_key": {"type": "string", "description": "Unique key for the space"},
                        "space_name": {"type": "string", "description": "Human-readable name of the space"},
                        "created_by_user_id": {"type": "string", "description": "ID of the user creating the space"},
                        "space_purpose": {"type": "string", "description": "Purpose/description of the space (optional)"}
                    },
                    "required": ["space_key", "space_name", "created_by_user_id"]
                }
            }
        }


class UpdateSpace(Tool):
    """
    Updates an existing space's fields (space_name, space_purpose).
    Resolves space by space_id or space_key.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        space_id: Optional[str] = None,
        space_key: Optional[str] = None,
        space_name: Optional[str] = None,
        space_purpose: Optional[str] = None
    ) -> str:
        spaces = data.get("spaces", {})

        if not space_id and not space_key:
            return json.dumps({"error": "Provide space_id or space_key"})

        # Locate record
        rec_key = None
        record = None
        if space_id:
            rec_key = str(space_id)
            record = spaces.get(rec_key)
        else:
            for k, v in spaces.items():
                if v.get("space_key") == space_key:
                    rec_key = k
                    record = v
                    break

        if not record:
            return json.dumps({"error": "Space not found"})

        # Validation: disallow empty name
        if space_name is not None and space_name.strip() == "":
            return json.dumps({"error": "Validation failure: space_name cannot be empty"})

        # Apply updates
        updated = dict(record)
        if space_name is not None:
            updated["space_name"] = space_name
        if space_purpose is not None:
            updated["space_purpose"] = space_purpose

        updated["updated_at"] = "2025-10-01T00:00:00"

        spaces[rec_key] = updated
        data["spaces"] = spaces
        return json.dumps(updated)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "update_space",
                "description": "Update an existing space identified by space_id or space_key.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "space_id": {"type": "string", "description": "ID of the space to update (optional if space_key provided)"},
                        "space_key": {"type": "string", "description": "Key of the space to update (optional if space_id provided)"},
                        "space_name": {"type": "string", "description": "New name for the space (cannot be empty)"},
                        "space_purpose": {"type": "string", "description": "New purpose/description for the space"}
                    },
                    "required": []
                }
            }
        }


class DeleteSpace(Tool):
    """
    Soft-deletes a space by marking is_deleted=True and setting deleted_at.
    """

    @staticmethod
    def invoke(
        data: Dict[str, Any],
        space_id: Optional[str] = None,
        space_key: Optional[str] = None
    ) -> str:
        spaces = data.get("spaces", {})

        if not space_id and not space_key:
            return json.dumps({"error": "Provide space_id or space_key"})

        # Find record
        rec_key = None
        record = None
        if space_id:
            rec_key = str(space_id)
            record = spaces.get(rec_key)
        else:
            for k, v in spaces.items():
                if v.get("space_key") == space_key:
                    rec_key = k
                    record = v
                    break

        if not record:
            return json.dumps({"error": "Space not found"})

        timestamp = "2025-10-01T00:00:00"
        updated = dict(record)
        updated["is_deleted"] = True
        updated["deleted_at"] = timestamp
        updated["updated_at"] = timestamp

        spaces[rec_key] = updated
        data["spaces"] = spaces
        return json.dumps(updated)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "delete_space",
                "description": "Soft delete a space by ID or key. Sets is_deleted=True and deleted_at.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "space_id": {"type": "string", "description": "ID of the space to delete (optional if space_key provided)"},
                        "space_key": {"type": "string", "description": "Key of the space to delete (optional if space_id provided)"}
                    },
                    "required": []
                }
            }
        }
