from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class NotificationStatus(str, Enum):
    SENT = "sent"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True)
class Notification:
    receiver_id: str
    message: str
    event: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class DeliveryResult:
    channel: str
    status: NotificationStatus
    detail: str | None = None
