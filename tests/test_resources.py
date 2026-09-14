from typing import Any, Dict, List, Optional

from notix import Notix


class MockResponse:
    def __init__(self, payload: Dict[str, Any], ok: bool = True, reason: str = "OK") -> None:
        self._payload = payload
        self.ok = ok
        self.reason = reason
        self.status_code = 200 if ok else 400

    def json(self) -> Dict[str, Any]:
        return self._payload


class MockSession:
    def __init__(self, responses: List[MockResponse]) -> None:
        self._responses = responses
        self.calls: List[Dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
    ) -> MockResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "json": json,
            }
        )
        return self._responses.pop(0)


def test_contact_books_list_uses_expected_path_and_returns_data() -> None:
    session = MockSession(
        [
            MockResponse(
                [
                    {
                        "id": "cb_123",
                        "name": "Newsletter Subscribers",
                        "teamId": 1,
                        "properties": {},
                        "variables": ["company"],
                        "emoji": "📙",
                        "doubleOptInEnabled": True,
                        "doubleOptInFrom": "Newsletter <hello@example.com>",
                        "doubleOptInSubject": "Please confirm your subscription",
                        "doubleOptInContent": "{}",
                        "createdAt": "2026-03-01T00:00:00.000Z",
                        "updatedAt": "2026-03-01T00:00:00.000Z",
                        "_count": {"contacts": 12},
                    }
                ]
            )
        ]
    )
    client = Notix("notix_test", session=session)

    data, err = client.contact_books.list()

    assert err is None
    assert data is not None
    assert data[0]["variables"] == ["company"]
    assert session.calls[0]["method"] == "GET"
    assert session.calls[0]["url"].endswith("/api/v1/contactBooks")


def test_contact_books_alias_matches_js_style_client() -> None:
    session = MockSession([MockResponse({"id": "cb_123", "name": "Book"})])
    client = Notix("notix_test", session=session)

    data, err = client.contactBooks.get("cb_123")

    assert err is None
    assert data is not None
    assert data["id"] == "cb_123"
    assert session.calls[0]["url"].endswith("/api/v1/contactBooks/cb_123")


def test_contacts_list_encodes_query_params() -> None:
    session = MockSession([MockResponse([])])
    client = Notix("notix_test", session=session)

    data, err = client.contacts.list(
        "cb_123",
        emails="a@example.com,b@example.com",
        page=2,
        limit=50,
        ids="ct_1,ct_2",
    )

    assert err is None
    assert data == []
    assert session.calls[0]["method"] == "GET"
    assert session.calls[0]["url"].endswith(
        "/api/v1/contactBooks/cb_123/contacts?emails=a%40example.com%2Cb%40example.com&page=2&limit=50&ids=ct_1%2Cct_2"
    )


def test_contacts_bulk_methods_use_expected_payloads() -> None:
    session = MockSession(
        [
            MockResponse({"message": "Contacts imported", "count": 2}),
            MockResponse({"success": True, "count": 2}),
        ]
    )
    client = Notix("notix_test", session=session)

    create_data, create_err = client.contacts.bulk_create(
        "cb_123",
        [
            {"email": "a@example.com"},
            {"email": "b@example.com", "firstName": "B"},
        ],
    )
    delete_data, delete_err = client.contacts.bulk_delete(
        "cb_123",
        {"contactIds": ["ct_1", "ct_2"]},
    )

    assert create_err is None
    assert create_data == {"message": "Contacts imported", "count": 2}
    assert delete_err is None
    assert delete_data == {"success": True, "count": 2}
    assert session.calls[0]["method"] == "POST"
    assert session.calls[0]["json"] == [
        {"email": "a@example.com"},
        {"email": "b@example.com", "firstName": "B"},
    ]
    assert session.calls[1]["method"] == "DELETE"
    assert session.calls[1]["json"] == {"contactIds": ["ct_1", "ct_2"]}


def test_sms_send_sets_idempotency_header(session_stub):
    notix = Notix("notix_test", session=session_stub({"id": "sms_1", "status": "queued"}))
    data, err = notix.sms.send({"to": "+2348012345678", "text": "Hi"}, idempotency_key="k1")
    assert err is None and data["id"] == "sms_1"
    assert session_stub.last.headers["Idempotency-Key"] == "k1"
    assert session_stub.last.url.endswith("/api/v1/sms")


def test_sms_send_without_an_idempotency_key_sends_no_header(session_stub):
    notix = Notix("notix_test", session=session_stub({"id": "sms_1", "status": "queued"}))
    notix.sms.send({"to": "+2348012345678", "text": "Hi"})
    assert "Idempotency-Key" not in session_stub.last.headers


def test_sms_get_reads_one_message(session_stub):
    notix = Notix("notix_test", session=session_stub({"id": "sms_1", "status": "delivered"}))
    data, err = notix.sms.get("sms_1")
    assert err is None and data["status"] == "delivered"
    assert session_stub.last.url.endswith("/api/v1/sms/sms_1")
    assert session_stub.last.method == "GET"


def test_sms_list_builds_query(session_stub):
    notix = Notix("notix_test", session=session_stub({"data": [], "nextCursor": None}))
    notix.sms.list(limit=10, status="failed")
    assert session_stub.last.url.endswith("/api/v1/sms?limit=10&status=failed")


def test_sms_list_with_no_query_hits_the_plain_path(session_stub):
    notix = Notix("notix_test", session=session_stub({"data": [], "nextCursor": None}))
    notix.sms.list()
    assert session_stub.last.url.endswith("/api/v1/sms")


def test_verify_send_with_channel(session_stub):
    notix = Notix("notix_test", session=session_stub({"id": "ver_1", "channel": "sms"}))
    data, err = notix.verify.send({"to": "+2348012345678", "channel": "sms", "appName": "Acme"})
    assert err is None and data["channel"] == "sms"
    assert session_stub.last.url.endswith("/api/v1/verify/send")


def test_verify_check_and_get_use_the_expected_paths(session_stub):
    notix = Notix("notix_test", session=session_stub({"verified": True}))
    notix.verify.check({"id": "ver_1", "code": "123456"})
    assert session_stub.last.url.endswith("/api/v1/verify/check")

    notix2 = Notix("notix_test", session=session_stub({"id": "ver_1", "status": "pending"}))
    notix2.verify.get("ver_1")
    assert session_stub.last.url.endswith("/api/v1/verify/ver_1")


def test_auth_check_reads_the_key(session_stub):
    notix = Notix("notix_test", session=session_stub({"ok": True, "teamId": 7, "keyId": 3, "permission": "SENDING"}))
    data, err = notix.auth.check()
    assert err is None and data["permission"] == "SENDING"
    assert session_stub.last.method == "GET"
    assert session_stub.last.url.endswith("/api/v1/auth/check")


def test_journeys_list_get_and_enroll_use_the_expected_paths(session_stub):
    notix = Notix("notix_test", session=session_stub([{"id": "jrn_1"}]))
    notix.journeys.list()
    assert session_stub.last.method == "GET"
    assert session_stub.last.url.endswith("/api/v1/journeys")

    notix = Notix("notix_test", session=session_stub({"id": "jrn_1"}))
    notix.journeys.get("jrn 1")
    assert session_stub.last.url.endswith("/api/v1/journeys/jrn%201")

    notix = Notix("notix_test", session=session_stub({"id": "run_1"}, 201))
    data, err = notix.journeys.enroll("jrn_1", {"email": "user@example.com"})
    assert err is None and data["id"] == "run_1"
    assert session_stub.last.method == "POST"
    assert session_stub.last.url.endswith("/api/v1/journeys/jrn_1/enroll")
    assert session_stub.last.json == {"email": "user@example.com"}


def test_deliverability_check_posts_the_message(session_stub):
    notix = Notix("notix_test", session=session_stub({"verdict": "PASS", "score": 98}))
    payload = {"from": "Acme <hello@acme.com>", "subject": "Hi", "html": "<p>Hi</p>"}
    data, err = notix.deliverability.check(payload)
    assert err is None and data["verdict"] == "PASS"
    assert session_stub.last.method == "POST"
    assert session_stub.last.url.endswith("/api/v1/deliverability/check")
    assert session_stub.last.json == payload


def test_analytics_build_their_queries(session_stub):
    notix = Notix("notix_test", session=session_stub({"result": [], "totalCounts": {}}))
    notix.analytics.email_time_series(days="7", domain_id="12")
    assert session_stub.last.url.endswith("/api/v1/analytics/email-time-series?days=7&domainId=12")

    notix = Notix("notix_test", session=session_stub({"result": [], "totalCounts": {}}))
    notix.analytics.email_time_series()
    assert session_stub.last.url.endswith("/api/v1/analytics/email-time-series")

    notix = Notix("notix_test", session=session_stub({"bounceRate": 0.01}))
    notix.analytics.reputation_metrics(domain_id="12")
    assert session_stub.last.url.endswith("/api/v1/analytics/reputation-metrics?domainId=12")


def test_segments_crud_uses_the_contact_book_paths() -> None:
    definition = {"version": 1, "match": "all", "conditions": [{"type": "subscribed", "op": "is", "value": True}]}
    session = MockSession(
        [
            MockResponse({"data": []}),
            MockResponse({"id": "seg_1", "name": "Subscribed"}),
            MockResponse({"id": "seg_1"}),
            MockResponse({"id": "seg_1", "name": "Renamed"}),
            MockResponse({"id": "seg_1", "deleted": True}),
        ]
    )
    client = Notix("notix_test", session=session)

    client.segments.list("cb_1")
    data, err = client.segments.create("cb_1", {"name": "Subscribed", "definition": definition})
    client.segments.get("cb_1", "seg_1")
    client.segments.update("cb_1", "seg_1", {"name": "Renamed"})
    client.segments.delete("cb_1", "seg_1")

    assert err is None
    assert data is not None and data["id"] == "seg_1"
    assert [(c["method"], c["url"].split("/api/v1")[1]) for c in session.calls] == [
        ("GET", "/contactBooks/cb_1/segments"),
        ("POST", "/contactBooks/cb_1/segments"),
        ("GET", "/contactBooks/cb_1/segments/seg_1"),
        ("PATCH", "/contactBooks/cb_1/segments/seg_1"),
        ("DELETE", "/contactBooks/cb_1/segments/seg_1"),
    ]
    assert session.calls[1]["json"] == {"name": "Subscribed", "definition": definition}
    assert session.calls[3]["json"] == {"name": "Renamed"}


def test_segment_contacts_encodes_cursor_and_limit() -> None:
    session = MockSession(
        [MockResponse({"data": [], "nextCursor": None, "total": 0}), MockResponse({"data": [], "nextCursor": None, "total": 0})]
    )
    client = Notix("notix_test", session=session)

    client.segments.contacts("cb_1", "seg_1", cursor="cnt_9", limit=20)
    client.segments.contacts("cb_1", "seg_1")

    assert session.calls[0]["url"].endswith("/api/v1/contactBooks/cb_1/segments/seg_1/contacts?cursor=cnt_9&limit=20")
    assert session.calls[1]["url"].endswith("/api/v1/contactBooks/cb_1/segments/seg_1/contacts")
