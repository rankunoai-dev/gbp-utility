"""Adapter tests against a fake HTTP session (no network, no Google SDK)."""

from typing import Any

import pytest

from core.adapters.gbp_api_adapter import (
    GBPApiAdapter,
    GBPApiError,
    apply_snapshot,
    format_address,
    parse_location,
)
from tests.conftest import make_client

LOCATION = {
    "name": "locations/1122334455",
    "title": "Childtime of Fairport",
    "storefrontAddress": {
        "regionCode": "US",
        "postalCode": "14450",
        "administrativeArea": "NY",
        "locality": "Fairport",
        "addressLines": ["585 Garnsey Rd"],
    },
    "websiteUri": "https://www.childtime.com/your-local-school/fairport-ny-0002/",
    "categories": {
        "primaryCategory": {
            "name": "categories/gcid:day_care_center",
            "displayName": "Day care center",
            "serviceTypes": [
                {"serviceTypeId": "job_type_id:infant_care", "displayName": "Infant care"},
                {"serviceTypeId": "job_type_id:toddler_care", "displayName": "Toddler care"},
            ],
        },
        "additionalCategories": [
            {
                "name": "categories/gcid:preschool",
                "displayName": "Preschool",
                "serviceTypes": [{"serviceTypeId": "job_type_id:pre_k", "displayName": "Pre-K"}],
            },
            {"name": "categories/gcid:child_care_agency", "displayName": "Child care agency"},
        ],
    },
    "serviceItems": [
        {"structuredServiceItem": {"serviceTypeId": "job_type_id:infant_care"}},
        {"structuredServiceItem": {"serviceTypeId": "job_type_id:toddler_care"}},
        {"structuredServiceItem": {"serviceTypeId": "job_type_id:pre_k"}},
        {"structuredServiceItem": {"serviceTypeId": "job_type_id:unknown_thing"}},
        {
            "freeFormServiceItem": {
                "category": "categories/gcid:day_care_center",
                "label": {"displayName": "Early Preschool", "languageCode": "en"},
            }
        },
        {
            "freeFormServiceItem": {
                "category": "categories/gcid:day_care_center",
                "label": {"displayName": "Before & After School Care"},
            }
        },
        {
            "freeFormServiceItem": {
                "category": "categories/gcid:day_care_center",
                "label": {"displayName": "early preschool"},
            }
        },
    ],
    "metadata": {"mapsUri": "https://maps.google.com/?cid=123", "placeId": "ChIJabc"},
}
REVIEWS = {
    "reviews": [{"reviewId": "x", "starRating": "FIVE"}],
    "averageRating": 4.6666,
    "totalReviewCount": 12,
}


class _Resp:
    def __init__(self, status: int, payload: Any) -> None:
        self.status_code = status
        self._payload = payload
        self.text = str(payload)

    def json(self) -> Any:
        return self._payload


class FakeSession:
    def __init__(self, routes: dict[str, Any]) -> None:
        self.routes = routes
        self.calls: list[tuple[str, dict[str, Any], dict[str, str]]] = []

    def get(
        self, url: str, *, headers: dict[str, str], params: dict[str, Any], timeout: float
    ) -> _Resp:
        self.calls.append((url, params, headers))
        for prefix, payload in self.routes.items():
            if url.startswith(prefix):
                if callable(payload):
                    return payload(params)
                return _Resp(200, payload)
        return _Resp(404, {"error": "no route"})


def test_parse_location_maps_categories_and_services() -> None:
    snap = parse_location(LOCATION)
    assert snap.location_id == "1122334455"
    assert snap.title == "Childtime of Fairport"
    assert snap.address == "585 Garnsey Rd, Fairport, NY 14450"
    assert snap.primary_category == "Day care center"
    assert snap.additional_categories == ["Preschool", "Child care agency"]
    # structured ids resolved via category serviceTypes; unknown id humanised; free-form deduped
    assert snap.services == [
        "Infant care",
        "Toddler care",
        "Pre-K",
        "Unknown Thing",
        "Early Preschool",
        "Before & After School Care",
    ]
    assert snap.maps_url == "https://maps.google.com/?cid=123"
    assert snap.place_id == "ChIJabc"


def test_format_address_handles_missing_parts() -> None:
    assert format_address({}) == ""
    assert (
        format_address({"addressLines": ["1 Main St", "Suite 2"], "locality": "Town"})
        == "1 Main St, Suite 2, Town"
    )


def test_fetch_location_combines_profile_and_rating() -> None:
    session = FakeSession(
        {
            "https://mybusinessbusinessinformation.googleapis.com/v1/locations/1122334455": LOCATION,
            "https://mybusiness.googleapis.com/v4/accounts/999/locations/1122334455/reviews": REVIEWS,
        }
    )
    adapter = GBPApiAdapter(session, lambda: "tok-123")
    snap = adapter.fetch_location("accounts/999", "locations/1122334455")
    assert snap.rating == 4.7 and snap.reviews_count == 12
    url, params, headers = session.calls[0]
    assert params["readMask"].startswith("name,title,")
    assert headers["Authorization"] == "Bearer tok-123"


def test_list_locations_paginates() -> None:
    def pages(params: dict[str, Any]) -> _Resp:
        if params.get("pageToken") == "p2":
            return _Resp(200, {"locations": [dict(LOCATION, name="locations/2", title="B")]})
        return _Resp(
            200,
            {"locations": [dict(LOCATION, name="locations/1", title="A")], "nextPageToken": "p2"},
        )

    session = FakeSession(
        {"https://mybusinessbusinessinformation.googleapis.com/v1/accounts/999/locations": pages}
    )
    locs = GBPApiAdapter(session, lambda: "t").list_locations("999")
    assert [loc.title for loc in locs] == ["A", "B"]
    assert len(session.calls) == 2


def test_non_200_raises() -> None:
    session = FakeSession({})
    with pytest.raises(GBPApiError):
        GBPApiAdapter(session, lambda: "t").list_accounts()


def test_apply_snapshot_overlays_gbp_fields_only() -> None:
    client = make_client(
        gbp_services=["Old Chip"], website_programs=["Infants", "Twos"], rating=3.0, reviews_count=1
    )
    snap = parse_location(LOCATION)
    snap.rating, snap.reviews_count = 4.7, 12
    merged = apply_snapshot(client, snap)
    assert merged.website_programs == ["Infants", "Twos"]  # untouched
    assert merged.gbp_services[:2] == ["Infant care", "Toddler care"]
    assert merged.primary_category == "Day care center"
    assert merged.additional_categories == ["Preschool", "Child care agency"]
    assert merged.rating == 4.7 and merged.reviews_count == 12
    assert merged.address == "585 Garnsey Rd, Fairport, NY 14450"
    assert merged.gbp_location_id == "1122334455"
    assert merged.school_name == client.school_name  # audit identity untouched


def test_apply_snapshot_never_erases_with_empty_values() -> None:
    client = make_client()
    empty = parse_location({"name": "locations/5"})
    merged = apply_snapshot(client, empty)
    assert merged.gbp_services == client.gbp_services
    assert merged.primary_category == client.primary_category
    assert merged.rating == client.rating
