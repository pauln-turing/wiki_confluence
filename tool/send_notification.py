
from base import Tool
from typing import Any, Dict
from data_manager import DataManager
import json

class SendNotification(Tool):
    @staticmethod
    def invoke(payload: Dict[str, Any], **kwargs) -> Any:
        # flat payload: recipient_user_id, event_type, message, related_entity_type (opt), related_entity_id (opt), channel (opt), sender_user_id (opt), metadata (opt)
        try:
            recipient_user_id = payload.get("recipient_user_id")
            event_type = payload.get("event_type")
            message = payload.get("message")
            related_entity_type = payload.get("related_entity_type")
            related_entity_id = payload.get("related_entity_id")
            channel = payload.get("channel")
            sender_user_id = payload.get("sender_user_id")
            metadata = payload.get("metadata")

            nid = DataManager.get_next_id("notifications")
            notification = {
                "recipient_user_id": recipient_user_id,
                "event_type": event_type,
                "message": message,
                "related_entity_type": related_entity_type,
                "related_entity_id": related_entity_id,
                "channel": channel,
                "sender_user_id": sender_user_id,
                "metadata": metadata,
                "created_at": DataManager.get_timestamp(),
            }
            DataManager.create_record("notifications", nid, notification)
            return json.dumps({"notification_id": nid, **notification})
        except Exception as e:
            return json.dumps({"error": str(e)})

    @staticmethod
    def get_info() -> dict[str, Any]:
        return {
            "tool_name": "send_notification",
            "category": "Notification Management",
            "description": "Sends a system or email notification to a user",
            "arguments": "table_name=\'notifications\', action=\'create\', payload={recipient_user_id: str, event_type: str, message: str, related_entity_type?: str, related_entity_id?: str, channel?: notification_channel, sender_user_id?: str, metadata?: json}",
            "flag": "Setter"
        }

