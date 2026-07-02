"""API views for the Group F notification demo."""
from __future__ import annotations

import json
from typing import Any, Dict, List

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import NotificationLog
from .patterns import AuditSubscriber, Message, NotificationService, build_channel_stack

VALID_CHANNELS = ("push", "sms", "email", "in-app")


def _json_body(request: HttpRequest) -> Dict[str, Any]:
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON request body.") from exc


def _clean_channels(raw_channels: Any) -> List[str]:
    if not isinstance(raw_channels, list):
        return []
    return [channel for channel in raw_channels if channel in VALID_CHANNELS]


@csrf_exempt
@require_POST
def send_notification(request: HttpRequest) -> JsonResponse:
    """Send one notification through the selected pattern-based channel stack."""

    try:
        data = _json_body(request)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    event_type = str(data.get("eventType", "System Alert")).strip() or "System Alert"
    body = str(data.get("message", "")).strip()
    recipient_email = str(data.get("email", "")).strip()
    recipient_phone = str(data.get("phone", "")).strip()
    selected_channels = _clean_channels(data.get("channels", ["push", "sms", "email"]))

    if not body:
        return JsonResponse({"error": "Message is required."}, status=400)
    if not selected_channels:
        return JsonResponse({"error": "Pick at least one valid channel."}, status=400)

    message = Message(
        event_type=event_type,
        body=body,
        recipient_email=recipient_email,
        recipient_phone=recipient_phone,
    )

    service = NotificationService()
    service.subscribe(AuditSubscriber())

    channels = [build_channel_stack(channel) for channel in selected_channels]
    result = service.notify(message, channels)

    log = NotificationLog.objects.create(
        event_type=event_type,
        recipient_email=recipient_email,
        recipient_phone=recipient_phone,
        message=body,
        selected_channels=", ".join(selected_channels),
        final_status="sent" if result.success else "failed",
        pattern_trace=message.trace,
    )

    return JsonResponse(
        {
            "id": log.id,
            "status": log.final_status,
            "winningChannel": result.channel,
            "detail": result.detail,
            "trace": message.trace,
        }
    )


@require_GET
def list_logs(request: HttpRequest) -> JsonResponse:
    """Return recent demo sends so the frontend can show history."""

    logs = NotificationLog.objects.all()[:15]
    return JsonResponse(
        {
            "logs": [
                {
                    "id": log.id,
                    "eventType": log.event_type,
                    "email": log.recipient_email,
                    "phone": log.recipient_phone,
                    "message": log.message,
                    "channels": log.selected_channels,
                    "status": log.final_status,
                    "trace": log.pattern_trace,
                    "createdAt": log.created_at.isoformat(),
                }
                for log in logs
            ]
        }
    )
