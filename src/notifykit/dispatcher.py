from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .base import Notifier
from .models import DeliveryResult, Notification, NotificationStatus


@dataclass(frozen=True)
class DispatchReport:
    notification: Notification
    results: Sequence[DeliveryResult]

    @property
    def ok(self) -> bool:
        # Consider "sent" or "skipped" as not an error; tune to your needs
        return all(r.status in (NotificationStatus.SENT, NotificationStatus.SKIPPED) for r in self.results)


class Dispatcher:
    """Sends a notification through one or more Notifier channels."""

    def __init__(self, channels: Iterable[Notifier]) -> None:
        self._channels = list(channels)

    def dispatch(self, notification: Notification) -> DispatchReport:
        results: list[DeliveryResult] = []
        for channel in self._channels:
            try:
                results.append(channel.send(notification))
            except Exception as exc:  # keep dispatcher robust
                results.append(
                    DeliveryResult(channel=channel.name, status=NotificationStatus.FAILED, detail=str(exc))
                )
        return DispatchReport(notification=notification, results=results)
