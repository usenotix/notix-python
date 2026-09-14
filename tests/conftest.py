"""Shared pytest fixtures for the resource tests in this directory."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Optional

import pytest


class _StubResponse:
    def __init__(self, payload: Any, status: int) -> None:
        self._payload = payload
        self.status_code = status
        self.ok = 200 <= status < 300
        self.reason = "OK" if self.ok else "Error"

    def json(self) -> Any:
        return self._payload


class SessionStub:
    """A ``requests.Session``-shaped stub.

    Calling the instance configures the response the next request receives
    and returns the instance itself, so it doubles as the ``session=``
    argument passed to ``Notix``. ``.last`` exposes the most recent request
    the client made, so a test can assert on its method, url, headers and
    body after the call.
    """

    def __init__(self) -> None:
        self._payload: Any = {}
        self._status = 200
        self.last: Optional[SimpleNamespace] = None

    def __call__(self, payload: Any, status: int = 200) -> "SessionStub":
        self._payload = payload
        self._status = status
        return self

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
    ) -> _StubResponse:
        self.last = SimpleNamespace(method=method, url=url, headers=headers or {}, json=json)
        return _StubResponse(self._payload, self._status)


@pytest.fixture
def session_stub() -> SessionStub:
    return SessionStub()
