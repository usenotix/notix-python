"""Segment resource client: saved, live filters on a contact book."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from urllib.parse import quote, urlencode

from .types import (
    APIError,
    Segment,
    SegmentContactsPage,
    SegmentCreate,
    SegmentDeleteResponse,
    SegmentList,
    SegmentUpdate,
)


def _segments_path(contact_book_id: str) -> str:
    return f"/contactBooks/{quote(contact_book_id, safe='')}/segments"


def _segment_path(contact_book_id: str, segment_id: str) -> str:
    return f"{_segments_path(contact_book_id)}/{quote(segment_id, safe='')}"


class Segments:
    """Client for `/contactBooks/{contactBookId}/segments` endpoints."""

    def __init__(self, notix: "Notix") -> None:
        self.notix = notix

    def list(self, contact_book_id: str) -> Tuple[Optional[SegmentList], Optional[APIError]]:
        data, err = self.notix.get(_segments_path(contact_book_id))
        return (data, err)  # type: ignore[return-value]

    def create(
        self, contact_book_id: str, payload: SegmentCreate
    ) -> Tuple[Optional[Segment], Optional[APIError]]:
        data, err = self.notix.post(_segments_path(contact_book_id), payload)
        return (data, err)  # type: ignore[return-value]

    def get(self, contact_book_id: str, segment_id: str) -> Tuple[Optional[Segment], Optional[APIError]]:
        data, err = self.notix.get(_segment_path(contact_book_id, segment_id))
        return (data, err)  # type: ignore[return-value]

    def update(
        self, contact_book_id: str, segment_id: str, payload: SegmentUpdate
    ) -> Tuple[Optional[Segment], Optional[APIError]]:
        data, err = self.notix.patch(_segment_path(contact_book_id, segment_id), payload)
        return (data, err)  # type: ignore[return-value]

    def delete(
        self, contact_book_id: str, segment_id: str
    ) -> Tuple[Optional[SegmentDeleteResponse], Optional[APIError]]:
        data, err = self.notix.delete(_segment_path(contact_book_id, segment_id))
        return (data, err)  # type: ignore[return-value]

    def contacts(
        self,
        contact_book_id: str,
        segment_id: str,
        *,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Tuple[Optional[SegmentContactsPage], Optional[APIError]]:
        """One page of the contacts matching the segment now; pass ``nextCursor`` back as ``cursor``."""
        query: Dict[str, Any] = {}
        if cursor is not None:
            query["cursor"] = cursor
        if limit is not None:
            query["limit"] = limit

        path = f"{_segment_path(contact_book_id, segment_id)}/contacts"
        if query:
            path = f"{path}?{urlencode(query)}"

        data, err = self.notix.get(path)
        return (data, err)  # type: ignore[return-value]


from .notix import Notix  # noqa: E402  pylint: disable=wrong-import-position
