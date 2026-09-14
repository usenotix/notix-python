"""Python client for the Notix API."""

from .notix import Notix, NotixHTTPError
from .auth import Auth  # type: ignore
from .analytics import Analytics  # type: ignore
from .deliverability import Deliverability  # type: ignore
from .journeys import Journeys  # type: ignore
from .contacts import Contacts  # type: ignore
from .contact_books import ContactBooks  # type: ignore
from .segments import Segments  # type: ignore
from .domains import Domains  # type: ignore
from .campaigns import Campaigns  # type: ignore
from .sms import Sms  # type: ignore
from .verify import Verify  # type: ignore
from .webhooks import (
    Webhooks,
    WebhookVerificationError,
    WEBHOOK_SIGNATURE_HEADER,
    WEBHOOK_TIMESTAMP_HEADER,
    WEBHOOK_EVENT_HEADER,
    WEBHOOK_CALL_HEADER,
)
from . import types

__all__ = [
    "Notix",
    "NotixHTTPError",
    "types",
    "Auth",
    "Analytics",
    "Deliverability",
    "Journeys",
    "Contacts",
    "ContactBooks",
    "Segments",
    "Domains",
    "Campaigns",
    "Sms",
    "Verify",
    "Webhooks",
    "WebhookVerificationError",
    "WEBHOOK_SIGNATURE_HEADER",
    "WEBHOOK_TIMESTAMP_HEADER",
    "WEBHOOK_EVENT_HEADER",
    "WEBHOOK_CALL_HEADER",
]
