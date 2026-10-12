"""Typed input schema for an audit run.

A dataset is a list of client schools, each with the entities discovered in
its territory. Validation here guarantees the engine never computes on a
malformed record (missing rating, empty category, unknown field...).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Classification = Literal["TRUE COMPETITOR", "SISTER BRAND (FILTERED)"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EntityProfile(_Strict):
    """Fields shared by the client school and every discovered entity."""

    name: str = Field(min_length=1)
    website_url: str = ""
    maps_url: str = ""
    address: str = Field(min_length=1)
    rating: float = Field(ge=0.0, le=5.0)
    reviews_count: int = Field(ge=0)
    primary_category: str = Field(min_length=1)
    additional_categories: list[str] = Field(default_factory=list)

    @property
    def all_categories(self) -> list[str]:
        """Primary category first, then the additional categories."""
        return [self.primary_category, *self.additional_categories]


class DiscoveredEntity(EntityProfile):
    """A business found in the client's territory (competitor or sister)."""

    brand_group: str = Field(min_length=1)
    distance_miles: float = Field(ge=0.0)
    services: list[str] = Field(default_factory=list)
    classification: Classification | None = None


class ClientSchool(EntityProfile):
    """The audited client location."""

    brand: str = Field(min_length=1)
    school_id: str = Field(min_length=1)
    school_name: str = Field(min_length=1)
    city: str = ""
    state: str = ""
    zip: str = ""
    phone: str = ""
    website_programs: list[str] = Field(default_factory=list)
    gbp_services: list[str] = Field(default_factory=list)
    # Business Profile API identifiers (``accounts/{id}`` / ``locations/{id}``
    # numeric parts). Required only when ``--client-source gbp-api`` is used.
    gbp_account_id: str = ""
    gbp_location_id: str = ""

    @field_validator("website_programs", "gbp_services")
    @classmethod
    def _dedupe(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in value:
            key = item.strip().lower()
            if key and key not in seen:
                seen.add(key)
                out.append(item.strip())
        return out


class SchoolAudit(_Strict):
    """One client school plus everything discovered around it."""

    client: ClientSchool
    discovered_entities: list[DiscoveredEntity] = Field(default_factory=list)


class AuditDataset(_Strict):
    """Top-level input document for a run."""

    client_brand: str = Field(min_length=1)
    client_brand_short: str = Field(min_length=1)
    schools: list[SchoolAudit] = Field(min_length=1)
