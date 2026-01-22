from __future__ import annotations

from ..base import Notifier
from ..models import DeliveryResult, Notification, NotificationStatus


class ConsoleNotifier(Notifier):
    @property
    def name(self) -> str:
        return "console"

    def send(self, notification: Notification) -> DeliveryResult:
        print(f"[notify:{self.name}] to={notification.receiver_id} msg={notification.message}")
        return DeliveryResult(channel=self.name, status=NotificationStatus.SENT)
