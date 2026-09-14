# Notix Python SDK

A minimal Python SDK for the [Notix](https://usenotix.dev) API, mirroring the structure of the JavaScript SDK.

## Installation

Install via pip or Poetry:

```
pip install notix-sdk
# or
poetry add notix-sdk
```

## Usage

```python
from notix import Notix, types

# By default: raises NotixHTTPError on non-2xx.
client = Notix("notix_123")

# 1) TypedDict payload (autocomplete in IDEs). Use dict to pass 'from'.
payload: types.EmailCreate = {
    "to": "test@example.com",
    "from": "no-reply@example.com",
    "subject": "Hello",
    "html": "<strong>Hi!</strong>",
}
resp, _ = client.emails.send(payload=payload)

# 2) Or pass a plain dict (supports 'from')
resp, _ = client.emails.send(payload={
    "to": "test@example.com",
    "from": "no-reply@example.com",
    "subject": "Hello",
    "html": "<strong>Hi!</strong>",
})

# Idempotent retries: same payload + same key returns the original response
resp, _ = client.emails.send(
    payload=payload,
    options={"idempotency_key": "signup-123"},
)

# Works for batch requests as well
resp, _ = client.emails.batch(
    payload=[payload],
    options={"idempotency_key": "bulk-welcome-1"},
)
# If the same key is reused with a different payload, the API responds with HTTP 409.

# 3) Campaigns
campaign_payload: types.CampaignCreate = {
    "name": "Welcome Series",
    "subject": "Welcome to our service!",
    "html": "<p>Thanks for joining us!</p>",
    "from": "welcome@example.com",
    "contactBookId": "cb_1234567890",
}
campaign_resp, _ = client.campaigns.create(payload=campaign_payload)

# Schedule a campaign
schedule_payload: types.CampaignSchedule = {
    "scheduledAt": "2024-12-01T10:00:00Z",
}
schedule_resp, _ = client.campaigns.schedule(
    campaign_id=campaign_resp["id"],
    payload=schedule_payload
)

# Pause/resume campaigns
client.campaigns.pause(campaign_id="campaign_123")
client.campaigns.resume(campaign_id="campaign_123")

# Toggle behavior if desired:
# - raise_on_error=False: return (None, error_dict) instead of raising
# No model parsing occurs; methods return plain dicts following the typed shapes.
client = Notix("notix_123", raise_on_error=False)
raw, err = client.emails.get(email_id="email_123")
if err:
    print("error:", err)
else:
    print("ok:", raw)
```

## SMS

Send a standalone transactional SMS. The message is charged to the team
wallet when it is queued; delivery status arrives through the `sms.*`
webhooks or a later `client.sms.get()`.

```python
data, err = client.sms.send(
    {"to": "+2348012345678", "text": "Your order 4471 has shipped."},
    idempotency_key="order-4471",
)

data, err = client.sms.get(data["id"])

data, err = client.sms.list(limit=10, status="failed")
```

`send`'s `idempotency_key` keyword makes a retry safe: the same key with the
same body returns the original message, and the same key with a different
body answers `NOT_UNIQUE`. `list` accepts `cursor`, `limit` and `status`
(`queued`, `sent`, `delivered`, `failed`, `rejected`).

Insufficient wallet balance answers `INSUFFICIENT_BALANCE`. With the default
`raise_on_error=True` this raises `NotixHTTPError`; with
`raise_on_error=False` it comes back as the `err` dict.

## Verification codes

Send a one-time code and check what the user typed:

```python
data, err = client.verify.send({"to": "user@example.com", "appName": "Acme"})

# Every send is risk scored. The level is LOW, MEDIUM or HIGH.
print(data["risk"]["level"])

data, err = client.verify.check({"id": data["id"], "code": "123456"})
if data["verified"]:
    ...

data, err = client.verify.get(data["id"])
```

Pass `channel: "sms"` to deliver the code by SMS instead of email:

```python
data, err = client.verify.send(
    {"to": "+2348012345678", "channel": "sms", "appName": "Acme"},
)
```

For `channel: "sms"`, `to` is a phone number in E.164 form, `appName` is
required, `senderId` is optional (defaults to the shared Notix sender ID),
and `from`, `subject` and `templateId` do not apply. The response carries
`channel`, `providerMessageId`, `deliveryStatus` and `deliveryReason`.

## Check an API key

```python
data, _ = client.auth.check()
# {"ok": True, "teamId": 7, "keyId": 3, "permission": "FULL" or "SENDING"}
```

## Segments

A segment is a saved, live filter on one contact book. Pass its id as
`segmentId` when you create a campaign to send only to the subscribed contacts
who match it when the send starts.

```python
segment, _ = client.segments.create(
    "cb_12345",
    {
        "name": "Engaged Pro users",
        "definition": {
            "version": 1,
            "match": "all",
            "conditions": [
                {"type": "property", "key": "plan", "op": "equals", "value": "Pro"},
                {"type": "email_activity", "event": "opened", "op": "in_last_days", "days": 30},
            ],
        },
    },
)

# Page through who matches right now.
cursor = None
while True:
    page, _ = client.segments.contacts("cb_12345", segment["id"], cursor=cursor, limit=100)
    for contact in page["data"]:
        print(contact["email"])
    cursor = page["nextCursor"]
    if cursor is None:
        break
```

## Journeys, deliverability and analytics

```python
# Enrol a contact into a journey, by contactId or by email in the journey's book
run, _ = client.journeys.enroll("jrn_123", {"email": "user@example.com"})

# Check a message before sending it
report, _ = client.deliverability.check({
    "from": "Acme <hello@acme.com>",
    "subject": "Your receipt",
    "html": "<p>Thanks for your order.</p>",
})
print(report["verdict"], report["score"])

# Email volume for the last 7 days, and reputation
series, _ = client.analytics.email_time_series(days="7")
reputation, _ = client.analytics.reputation_metrics()
```

## Webhook Local Example

For a runnable webhook verification demo project, see:

- `example/webhook-test-project/README.md`

## Development

This package is managed with Poetry. Models are maintained in-repo under
`notix/types.py` (readable names). Update this file as the API evolves.

It is published as `notix-sdk` on PyPI (the name `notix` belongs to an unrelated project). The import name is `notix`.

## Available Resources

- **Auth**: `client.auth.check()`
- **Emails**: `client.emails.send()`, `client.emails.get()`
- **ContactBooks**: `client.contact_books.list()`, `client.contact_books.create()`, `client.contact_books.get()`, `client.contact_books.update()`
- **Segments**: `client.segments.list()`, `client.segments.create()`, `client.segments.get()`, `client.segments.update()`, `client.segments.delete()`, `client.segments.contacts()`
- **Contacts**: `client.contacts.create()`, `client.contacts.list()`, `client.contacts.get()`, `client.contacts.bulk_create()`, `client.contacts.bulk_delete()`
- **Domains**: `client.domains.create()`, `client.domains.get()`, `client.domains.verify()`
- **Campaigns**: `client.campaigns.create()`, `client.campaigns.get()`, `client.campaigns.schedule()`, `client.campaigns.pause()`, `client.campaigns.resume()`
- **Sms**: `client.sms.send()`, `client.sms.get()`, `client.sms.list()`
- **Verify**: `client.verify.send()`, `client.verify.check()`, `client.verify.get()`
- **Journeys**: `client.journeys.list()`, `client.journeys.get()`, `client.journeys.enroll()`
- **Deliverability**: `client.deliverability.check()`
- **Analytics**: `client.analytics.email_time_series()`, `client.analytics.reputation_metrics()`

The full API reference is at [usenotix.dev/docs/reference](https://usenotix.dev/docs/reference).

Notes

- Human-friendly models are available under `notix.types` (e.g., `EmailCreate`, `CampaignCreate`, `Contact`, `APIError`).
- Endpoint methods accept TypedDict payloads or plain dicts via the `payload=` keyword.

## Issues and source

The source for this SDK is public at [github.com/usenotix/notix-python](https://github.com/usenotix/notix-python). Report a bug or ask for a feature in its [issues](https://github.com/usenotix/notix-python/issues). For account or delivery questions, write to hey@usenotix.dev.
