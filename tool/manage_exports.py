
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class ManageExports(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        action = kwargs.get("action")
        try:
            if action == "create":
                # flat payload: space_id, format, file_path(optional), conflict_resolution_strategy(optional)
                space_id = payload.get("space_id")
                fmt = payload.get("format")
                file_path = payload.get("file_path")
                conflict = payload.get("conflict_resolution_strategy")
                job = {"space_id": space_id, "format": fmt, "file_path": file_path, "conflict_resolution_strategy": conflict, "created_at": DataManager.get_timestamp()}
                job_id = DataManager.get_next_id("export_jobs")
                DataManager.create_record("export_jobs", job_id, job)
                return json.dumps({"job_id": job_id, **job})

            if action == "get":
                job_id = payload.get("job_id")
                if not job_id:
                    return json.dumps({"error": "'job_id' is required"})
                job = DataManager.get_record("export_jobs", str(job_id))
                return json.dumps(job if job else {"error": "Job not found."})

            return json.dumps({"error": "Unsupported or missing action. Use create/get."})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "manage_exports",
            "category": "Export Management",
            "description": "Creates a space export job, imports a space from a file, or retrieves export job status.",
            "arguments": "table_name=\'export_jobs\', action=\'create/import/get\', payload={space_id?: str, format?: export_format, file?: file, conflict_resolution_strategy?: str, job_id?: str}",
            "flag": "Setter"
        }

