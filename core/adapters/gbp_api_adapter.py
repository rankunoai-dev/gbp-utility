"""Official Google Business Profile API adapter (client-side data only).

Pulls the authoritative profile for a location the agency manages:
title, address, website, Maps URL, primary + additional categories, service
items, average rating and review count. Competitors are NOT reachable here
(the API only returns locations you own or manage).

Endpoints (all need an OAuth 2.0 token with the ``business.manage`` scope):

* Business Information API v1
    GET /v1/accounts/{account}/locations?readMask=...   (list, discover IDs)
    GET /v1/locations/{location}?readMask=...           (one location)
* Account Management API v1
    GET /v1/accounts                                     (discover accounts)
* Legacy My Business API v4 (still the only source of aggregate rating)
    GET /v4/accounts/{account}/locations/{location}/reviews?pageSize=1
        -> averageRating, totalReviewCount

Nothing here imports Google SDKs; a ``TokenProvider`` callable supplies the
bearer token, so the adapter is unit-testable with a fake session.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from core.models import ClientSchool

BUSINESS_INFO = "https://mybusinessbusinessinformation.googleapis.com/v1"
ACCOUNT_MGMT = "https://mybusinessaccountmanagement.googleapis.com/v1"
LEGACY_V4 = "https://mybusiness.googleapis.com/v4"

LOCATION_READ_MASK = "name,title,storefrontAddress,websiteUri,categories,serviceItems,metadata"

TokenProvider = Callable[[], str]


class _Session(Protocol):
    def get(
        self, url: str, *, headers: dict[str, str], params: dict[str, Any], timeout: float
    ) -> Any: ...


class GBPApiError(RuntimeError):
    """Raised when the API answers with a non-2xx status."""


@dataclass
class GBPLocationSnapshot:
    """Normalised view of one managed location."""

    location_id: str
    title: str
    address: str
    website_url: str
    maps_url: str
    place_id: str
    primary_category: str
    additional_categories: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    rating: float | None = None
    reviews_count: int | None = None


class GBPApiAdapter:
    """Thin, typed client over the three Business Profile endpoints we need."""

    def __init__(
        self, session: _Session, token_provider: TokenProvider, timeout: float = 30.0
    ) -> None:
        self.session = session
        self.token_provider = token_provider
        self.timeout = timeout

    # ------------------------------------------------------------------ HTTP
    def _get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.token_provider()}"}
        resp = self.session.get(url, headers=headers, params=params or {}, timeout=self.timeout)
        if resp.status_code != 200:
            raise GBPApiError(f"{resp.status_code} from {url}: {resp.text[:300]}")
        data: dict[str, Any] = resp.json()
        return data

    def _paginate(self, url: str, params: dict[str, Any], key: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        token: str | None = None
        while True:
            page = self._get(url, {**params, **({"pageToken": token} if token else {})})
            items.extend(page.get(key, []))
            token = page.get("nextPageToken")
            if not token:
                return items

    # ------------------------------------------------------------- discovery
    def list_accounts(self) -> list[dict[str, Any]]:
        """All accounts visible to the authorised user (``accounts/123``)."""
        return self._paginate(f"{ACCOUNT_MGMT}/accounts", {"pageSize": 20}, "accounts")

    def list_locations(self, account_id: str) -> list[GBPLocationSnapshot]:
        """Every location under ``account_id`` (numeric id or ``accounts/123``)."""
        account = account_id if account_id.startswith("accounts/") else f"accounts/{account_id}"
        raw = self._paginate(
            f"{BUSINESS_INFO}/{account}/locations",
            {"readMask": LOCATION_READ_MASK, "pageSize": 100},
            "locations",
        )
        return [parse_location(loc) for loc in raw]

    # --------------------------------------------------------------- fetch
    def fetch_location(self, account_id: str, location_id: str) -> GBPLocationSnapshot:
        """Profile + rating for one location."""
        loc_id = location_id.split("/")[-1]
        snap = parse_location(
            self._get(f"{BUSINESS_INFO}/locations/{loc_id}", {"readMask": LOCATION_READ_MASK})
        )
        snap.rating, snap.reviews_count = self.fetch_rating(account_id, loc_id)
        return snap

    def fetch_rating(self, account_id: str, location_id: str) -> tuple[float | None, int | None]:
        """Average rating and total review count from the v4 reviews endpoint."""
        acct = account_id.split("/")[-1]
        loc = location_id.split("/")[-1]
        data = self._get(f"{LEGACY_V4}/accounts/{acct}/locations/{loc}/reviews", {"pageSize": 1})
        rating = data.get("averageRating")
        count = data.get("totalReviewCount")
        return (
            round(float(rating), 1) if rating is not None else None,
            int(count) if count is not None else None,
        )


# ---------------------------------------------------------------- parsing
def parse_location(loc: dict[str, Any]) -> GBPLocationSnapshot:
    """Map a raw ``Location`` resource onto :class:`GBPLocationSnapshot`."""
    cats = loc.get("categories") or {}
    primary = cats.get("primaryCategory") or {}
    additional = cats.get("additionalCategories") or []

    # serviceTypeId -> display name, taken from every category's serviceTypes[]
    type_names: dict[str, str] = {}
    for cat in [primary, *additional]:
        for st in cat.get("serviceTypes") or []:
            if st.get("serviceTypeId") and st.get("displayName"):
                type_names[st["serviceTypeId"]] = st["displayName"]

    services: list[str] = []
    for item in loc.get("serviceItems") or []:
        if "structuredServiceItem" in item:
            sid = item["structuredServiceItem"].get("serviceTypeId", "")
            services.append(type_names.get(sid, _humanize_service_type(sid)))
        elif "freeFormServiceItem" in item:
            label = (item["freeFormServiceItem"].get("label") or {}).get("displayName", "")
            if label:
                services.append(label)

    meta = loc.get("metadata") or {}
    return GBPLocationSnapshot(
        location_id=str(loc.get("name", "")).split("/")[-1],
        title=loc.get("title", ""),
        address=format_address(loc.get("storefrontAddress") or {}),
        website_url=loc.get("websiteUri", ""),
        maps_url=meta.get("mapsUri", ""),
        place_id=meta.get("placeId", ""),
        primary_category=primary.get("displayName", ""),
        additional_categories=[
            c.get("displayName", "") for c in additional if c.get("displayName")
        ],
        services=_dedupe(services),
    )


def format_address(addr: dict[str, Any]) -> str:
    """``PostalAddress`` -> "585 Garnsey Rd, Fairport, NY 14450"."""
    lines = [ln.strip() for ln in addr.get("addressLines") or [] if ln and ln.strip()]
    locality = (addr.get("locality") or "").strip()
    region = (addr.get("administrativeArea") or "").strip()
    postal = (addr.get("postalCode") or "").strip()
    tail = " ".join(p for p in (region, postal) if p)
    parts = [*lines, locality, tail]
    return ", ".join(p for p in parts if p)


def _humanize_service_type(service_type_id: str) -> str:
    # e.g. "job_type_id:infant_care" -> "Infant Care"
    tail = service_type_id.split(":")[-1]
    return " ".join(w.capitalize() for w in tail.replace("-", "_").split("_") if w)


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        key = it.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(it.strip())
    return out


# ---------------------------------------------------------------- overlay
def apply_snapshot(client: ClientSchool, snap: GBPLocationSnapshot) -> ClientSchool:
    """Return a copy of ``client`` with GBP-sourced fields replaced by the API values.

    Website programs are deliberately untouched (they come from the school
    website, not GBP). Empty API values never erase dataset values.
    """
    update: dict[str, Any] = {
        "gbp_services": snap.services or client.gbp_services,
        "primary_category": snap.primary_category or client.primary_category,
        "additional_categories": snap.additional_categories or client.additional_categories,
        "address": snap.address or client.address,
        "website_url": snap.website_url or client.website_url,
        "maps_url": snap.maps_url or client.maps_url,
        "gbp_location_id": snap.location_id or client.gbp_location_id,
    }
    if snap.rating is not None:
        update["rating"] = snap.rating
    if snap.reviews_count is not None:
        update["reviews_count"] = snap.reviews_count
    return client.model_copy(update=update)
