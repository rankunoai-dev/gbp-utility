"""Shared fixtures. No test here touches the network."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.dataset import load_dataset  # noqa: E402
from core.gap_engine import GapEngine  # noqa: E402
from core.models import AuditDataset, ClientSchool, DiscoveredEntity, SchoolAudit  # noqa: E402

PILOT_DATASET = ROOT / "data" / "childtime_pilot_dataset.json"
REFERENCE_XLSX = ROOT / "Childtime_GBP_MultiBrand_Audit_Verified_Live.xlsx"


@pytest.fixture(scope="session")
def pilot_dataset() -> AuditDataset:
    return load_dataset(PILOT_DATASET)


@pytest.fixture
def engine() -> GapEngine:
    return GapEngine(brand_short="Childtime")


def make_entity(name: str, services: list[str], **overrides: object) -> DiscoveredEntity:
    base: dict[str, object] = {
        "brand_group": name.split()[0],
        "name": name,
        "website_url": f"https://{name.split()[0].lower()}.example.com/",
        "maps_url": "",
        "address": "1 Main St, Town, NY 10000",
        "distance_miles": 1.0,
        "rating": 4.5,
        "reviews_count": 10,
        "primary_category": "Day care center",
        "additional_categories": ["Preschool"],
        "services": services,
    }
    base.update(overrides)
    return DiscoveredEntity.model_validate(base)


def make_client(**overrides: object) -> ClientSchool:
    base: dict[str, object] = {
        "brand": "Childtime Learning Centers",
        "school_id": "9999",
        "school_name": "Childtime of Testville",
        "name": "Childtime of Testville",
        "website_url": "https://www.childtime.com/your-local-school/testville-ny-9999/",
        "maps_url": "",
        "address": "9 Test Rd, Testville, NY 10001",
        "rating": 4.5,
        "reviews_count": 20,
        "primary_category": "Day care center",
        "additional_categories": ["Preschool"],
        "website_programs": ["Infants", "Preschool", "Summer Camp", "Grow Fit"],
        "gbp_services": ["Infant Care"],
    }
    base.update(overrides)
    return ClientSchool.model_validate(base)


@pytest.fixture
def small_audit() -> SchoolAudit:
    """3 true competitors + 1 sister brand; designed to hit every tier.

    Expected per-service outcome (client web: Infants, Preschool, Summer Camp,
    Grow Fit; client GBP: Infant Care):
      Infant Care 3/3 DEFEND | Preschool Program 3/3 CRITICAL | Summer Camp 2/3
      CRITICAL | Grow Fit 0/3 INTERNAL | Pre-K 2/3 MARKET | Private Kindergarten
      1/3 MONITOR | Toddler Care 1/3 MONITOR. Category "Child care agency" 2/3
      CRITICAL.
    """
    return SchoolAudit(
        client=make_client(),
        discovered_entities=[
            make_entity(
                "Alpha Academy",
                ["Infant Care", "Preschool Program", "Summer Camp", "Kindergarten", "Pre-K"],
            ),
            make_entity(
                "Beta Kids",
                ["Infants", "Preschool", "Toddler Care", "Summer Camp", "Pre-Kindergarten"],
                additional_categories=["Preschool", "Child care agency"],
                rating=4.9,
                reviews_count=50,
            ),
            make_entity(
                "Gamma Center",
                ["Infant Care", "Preschool Program"],
                additional_categories=["Preschool", "Child care agency"],
            ),
            make_entity(
                "La Petite Academy of Testville",
                ["Infant Care", "Preschool", "Summer Camp", "Grow Fit"],
                website_url="https://www.lapetite.com/x/",
            ),
        ],
    )
