from __future__ import annotations

from dataclasses import dataclass
import requests

from ..base import Notifier
from ..models import DeliveryResult, Notification, NotificationStatus


@dataclass(frozen=True)
class WebhookConfig:
    url: str
    timeout_s: float = 5.0
    auth_header: str | None = None  # e.g. "Bearer <token>" (use placeholders)


class WebhookNotifier(Notifier):
    def __init__(self, config: WebhookConfig) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return "webhook"

    def send(self, notification: Notification) -> DeliveryResult:
        headers = {"Content-Type": "application/json"}
        if self._config.auth_header:
            headers["Authorization"] = self._config.auth_header

        payload = {
            "receiver_id": notification.receiver_id,
            "message": notification.message,
            "event": notification.event,
            "metadata": dict(notification.metadata or {}),
        }

        resp = requests.post(
            self._config.url,
            json=payload,
            headers=headers,
            timeout=self._config.timeout_s,
        )

        if 200 <= resp.status_code < 300:
            return DeliveryResult(channel=self.name, status=NotificationStatus.SENT, detail=f"HTTP {resp.status_code}")

        return DeliveryResult(
            channel=self.name,
            status=NotificationStatus.FAILED,
            detail=f"HTTP {resp.status_code}: {resp.text[:200]}",
        )