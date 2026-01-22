from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from ..base import Notifier
from ..models import DeliveryResult, Notification, NotificationStatus


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str                  # e.g. "<telegram-bot-token>"
    default_chat_id: str | None = None  # e.g. "<chat-id>"
    timeout_s: float = 10.0
    parse_mode: str | None = None   # "MarkdownV2" or "HTML" (optional)
    disable_web_page_preview: bool = True


class TelegramNotifier(Notifier):
    """
    Sends notifications using Telegram Bot API.

    How receiver mapping works:
    - If notification.metadata contains "chat_id", it is used.
    - Else TelegramConfig.default_chat_id is used.
    - Else sending is skipped (status=SKIPPED).
    """

    def __init__(self, config: TelegramConfig) -> None:
        self._config = config

    @property
    def name(self) -> str:
        return "telegram"

    def send(self, notification: Notification) -> DeliveryResult:
        chat_id = None
        if notification.metadata:
            chat_id = notification.metadata.get("chat_id")
        chat_id = chat_id or self._config.default_chat_id

        if not chat_id:
            return DeliveryResult(
                channel=self.name,
                status=NotificationStatus.SKIPPED,
                detail="Missing chat_id (set metadata['chat_id'] or TelegramConfig.default_chat_id).",
            )

        url = f"https://api.telegram.org/bot{self._config.bot_token}/sendMessage"

        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": notification.message,
            "disable_web_page_preview": self._config.disable_web_page_preview,
        }
        if self._config.parse_mode:
            payload["parse_mode"] = self._config.parse_mode

        resp = requests.post(url, json=payload, timeout=self._config.timeout_s)

        # Telegram returns JSON like: {"ok": true, "result": {...}} or {"ok": false, "description": "..."}
        try:
            data = resp.json()
        except Exception:
            data = None

        if resp.ok and isinstance(data, dict) and data.get("ok") is True:
            return DeliveryResult(channel=self.name, status=NotificationStatus.SENT, detail="ok")

        if isinstance(data, dict):
            detail = data.get("description") or str(data)[:200]
        else:
            detail = f"HTTP {resp.status_code}: {resp.text[:200]}"

        return DeliveryResult(channel=self.name, status=NotificationStatus.FAILED, detail=detail)