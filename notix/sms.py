"""SMS resource client using TypedDict shapes (no Pydantic)."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

from .types import APIError, SmsList, SmsMessage, SmsSend


class Sms:
    """Client for `/sms` endpoints.

    `send` charges the team wallet when the message is queued; delivery
    status arrives through the `sms.*` webhooks or a later `get`.
    """

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def send(
        self,
        payload: SmsSend,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[Optional[SmsMessage], Optional[APIError]]:
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        data, err = self.notix.post("/sms", payload, headers=headers)
        return (data, err)  # type: ignore[return-value]

    def get(self, sms_id: str) -> Tuple[Optional[SmsMessage], Optional[APIError]]:
        data, err = self.notix.get(f"/sms/{sms_id}")
        return (data, err)  # type: ignore[return-value]

    def list(
        self,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Tuple[Optional[SmsList], Optional[APIError]]:
        params: Dict[str, Any] = {}
        if cursor is not None:
            params["cursor"] = cursor
        if limit is not None:
            params["limit"] = limit
        if status is not None:
            params["status"] = status

        query = urlencode(params)
        path = f"/sms?{query}" if query else "/sms"
        data, err = self.notix.get(path)
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
