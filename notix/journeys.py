"""Journeys resource: list journeys and enrol contacts into them."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from .types import APIError


class Journeys:
    """Client for `/journeys` endpoints."""

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def list(self) -> Tuple[Optional[List[Dict[str, Any]]], Optional[APIError]]:
        """List the team's journeys, newest first."""
        data, err = self.notix.get("/journeys")
        return (data, err)  # type: ignore[return-value]

    def get(self, journey_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Return one journey and its stats."""
        data, err = self.notix.get(f"/journeys/{quote(journey_id, safe='')}")
        return (data, err)  # type: ignore[return-value]

    def enroll(
        self, journey_id: str, payload: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Enrol a contact by ``contactId`` or by ``email`` within the journey's contact book.

        Provide exactly one of the two. A contact holds at most one run per
        journey, so enrolling it again answers ``NOT_UNIQUE``.
        """
        data, err = self.notix.post(f"/journeys/{quote(journey_id, safe='')}/enroll", payload)
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
