"""Contact book resource client using TypedDict shapes (no Pydantic)."""
from __future__ import annotations

from typing import Optional, Tuple, List

from .types import (
    APIError,
    ContactBook,
    ContactBookCreate,
    ContactBookCreateResponse,
    ContactBookDeleteResponse,
    ContactBookUpdate,
    ContactBookUpdateResponse,
)


class ContactBooks:
    """Client for `/contactBooks` endpoints."""

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def list(self) -> Tuple[Optional[List[ContactBook]], Optional[APIError]]:
        data, err = self.notix.get("/contactBooks")
        return (data, err)  # type: ignore[return-value]

    def create(
        self, payload: ContactBookCreate
    ) -> Tuple[Optional[ContactBookCreateResponse], Optional[APIError]]:
        data, err = self.notix.post("/contactBooks", payload)
        return (data, err)  # type: ignore[return-value]

    def get(self, contact_book_id: str) -> Tuple[Optional[ContactBook], Optional[APIError]]:
        data, err = self.notix.get(f"/contactBooks/{contact_book_id}")
        return (data, err)  # type: ignore[return-value]

    def update(
        self, contact_book_id: str, payload: ContactBookUpdate
    ) -> Tuple[Optional[ContactBookUpdateResponse], Optional[APIError]]:
        data, err = self.notix.patch(f"/contactBooks/{contact_book_id}", payload)
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, contact_book_id: str
    ) -> Tuple[Optional[ContactBookDeleteResponse], Optional[APIError]]:
        data, err = self.notix.delete(f"/contactBooks/{contact_book_id}")
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
