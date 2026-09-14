"""Analytics resource: email volume over time and reputation metrics."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

from .types import APIError


def _with_query(path: str, params: Dict[str, Optional[str]]) -> str:
    query = urlencode({key: value for key, value in params.items() if value})
    return f"{path}?{query}" if query else path


class Analytics:
    """Client for `/analytics` endpoints."""

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def email_time_series(
        self, days: Optional[str] = None, domain_id: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Daily email counts by outcome for the last ``"7"`` or ``"30"`` days (30 by default)."""
        path = _with_query("/analytics/email-time-series", {"days": days, "domainId": domain_id})
        data, err = self.notix.get(path)
        return (data, err)  # type: ignore[return-value]

    def reputation_metrics(
        self, domain_id: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Delivered, hard-bounced and complained counts with bounce and complaint rates."""
        path = _with_query("/analytics/reputation-metrics", {"domainId": domain_id})
        data, err = self.notix.get(path)
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
