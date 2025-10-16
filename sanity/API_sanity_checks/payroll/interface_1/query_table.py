import json
import os
from typing import Any, Dict, Optional
from base import Tool


class QueryTable(Tool):
    @staticmethod
    def _invoke_internal(payload: Dict[str, Any], db: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        table = payload.get("data")
        filters = payload.get("filters") or {}

        if not table:
            return {"success": False, "error": "missing_table"}

        if db is not None:
            rows = db.get(table, [])
        else:
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(workspace_root, "data")
            path = os.path.join(data_dir, f"{table}")
            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                else:
                    raw = []
            except Exception as e:
                return {"success": False, "error": "read_error", "details": str(e)}

            if isinstance(raw, list):
                rows = raw
            elif isinstance(raw, dict):
                rows = list(raw.values())
            else:
                rows = []

        # apply simple equality filters
        def match(row: Dict[str, Any]) -> bool:
            for k, v in filters.items():
                if row.get(k) != v:
                    return False
            return True

        results = [r for r in rows if match(r)]
        return {"success": True, "results": results}

    @staticmethod
    def invoke(data: Dict[str, Any], table: str, filters: dict | None = None) -> str:
        try:
            payload = {"data": table, "filters": filters or {}}
            res = QueryTable._invoke_internal(payload, db=data)
        except Exception as e:
            return json.dumps({"success": False, "error": "internal_error", "details": str(e)})
        return json.dumps(res)

    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "query_table",
                "description": "Query an arbitrary data table by equality filters. Expects data dict, table filename, and optional filters dict.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "dict", "description": "In-memory DB"},
                        "table": {"type": "string"},
                        "filters": {"type": "object"}
                    },
                    "required": ["data", "table"]
                }
            }
        }
