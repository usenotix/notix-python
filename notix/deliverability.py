"""Deliverability resource: check a message before sending it."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .types import APIError


class Deliverability:
    """Client for `/deliverability/check`."""

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def check(self, payload: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Return a report with a verdict, a score and the findings for a message.

        Pass either ``html`` or ``templateId``, with ``from`` and ``subject``.
        A ``BLOCK`` verdict describes a message the send paths would refuse.
        """
        data, err = self.notix.post("/deliverability/check", payload)
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
