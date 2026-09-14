"""Auth resource: check the API key the client was created with."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .types import APIError


class Auth:
    """Client for `/auth/check`."""

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def check(self) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """Return the team, key id and permission (``FULL`` or ``SENDING``) of the key.

        Grants nothing, so a sending access key may call it too.
        """
        data, err = self.notix.get("/auth/check")
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
