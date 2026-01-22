from __future__ import annotations

from abc import ABC, abstractmethod
from typing import final

from .models import DeliveryResult, Notification


class Notifier(ABC):
    """Base class for notification providers (a.k.a. channels)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human/identifier name of the channel (e.g. 'email', 'slack')."""

    @abstractmethod
    def send(self, notification: Notification) -> DeliveryResult:
        """Send a notification through this channel."""

    @final
    def __call__(self, receiver_id: str, message: str) -> DeliveryResult:
        """Convenience call style: channel(receiver_id, message)."""
        return self.send(Notification(receiver_id=receiver_id, message=message))

