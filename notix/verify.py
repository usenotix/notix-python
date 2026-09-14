"""Verification resource client using TypedDict shapes (no Pydantic)."""
from __future__ import annotations

from typing import Optional, Tuple

from .types import APIError, Verification, VerificationCheck, VerificationSend


class Verify:
    """Client for `/verify` endpoints.

    Every send is risk scored. `channel` defaults to `email`; pass
    `channel: "sms"` with `to` as an E.164 phone number and `appName` set to
    deliver the code by SMS instead.
    """

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def send(
        self,
        payload: VerificationSend,
    ) -> Tuple[Optional[Verification], Optional[APIError]]:
        data, err = self.notix.post("/verify/send", payload)
        return (data, err)  # type: ignore[return-value]

    def check(
        self,
        payload: VerificationCheck,
    ) -> Tuple[Optional[Verification], Optional[APIError]]:
        data, err = self.notix.post("/verify/check", payload)
        return (data, err)  # type: ignore[return-value]

    def get(self, verification_id: str) -> Tuple[Optional[Verification], Optional[APIError]]:
        data, err = self.notix.get(f"/verify/{verification_id}")
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
