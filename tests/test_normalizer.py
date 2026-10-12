import pytest

from core.normalizer import Normalizer
from core.taxonomy import CORE_PROGRAMS, SERVICE_SYNONYMS


@pytest.fixture(scope="module")
def norm() -> Normalizer:
    return Normalizer()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Infants", "Infant Care"),
        ("  infant care ", "Infant Care"),
        ("Toddler Program", "Toddler Care"),
        ("Discovery Preschool", "Early Preschool"),
        ("Preschool", "Preschool Program"),
        ("Pre-Kindergarten", "Pre-K"),
        ("Pre-K Readiness", "Pre-K"),
        ("Kindergarten", "Private Kindergarten"),
        ("Before & After School", "Before and After School"),
        ("Before & After School Care", "Before and After School"),
        ("Summer Program", "Summer Camp"),
        ("Enrichment Arts & Music", "Electives"),
        ("Nutritious Meals", None),
        ("F.L.EX. Learning Program", None),
        ("", None),
    ],
)
def test_canonical_service(norm: Normalizer, raw: str, expected: str | None) -> None:
    assert norm.canonical_service(raw) == expected


def test_every_synonym_targets_a_core_program() -> None:
    assert set(SERVICE_SYNONYMS.values()) <= set(CORE_PROGRAMS)


def test_order_raw_programs_follows_taxonomy_then_alpha(norm: Normalizer) -> None:
    raw = ["Summer Camp", "Zeta Thing", "Infants", "Alpha Thing", "Preschool"]
    assert norm.order_raw_programs(raw) == ["Infants", "Preschool", "Summer Camp", "Alpha Thing", "Zeta Thing"]


@pytest.mark.parametrize(
    ("count", "total", "expected"),
    [(2, 3, 67), (4, 6, 67), (1, 6, 17), (1, 8, 13), (0, 5, 0), (5, 5, 100), (3, 0, 0)],
)
def test_pct_half_up(norm: Normalizer, count: int, total: int, expected: int) -> None:
    assert norm.pct(count, total) == expected


@pytest.mark.parametrize(
    ("name", "url", "expected"),
    [
        ("La Petite Academy of Victor", "https://www.lapetite.com/x", True),
        ("Tutor Time Child Care", "", True),
        ("Some School", "https://www.childtime.com/y", True),
        ("The Goddard School", "https://www.goddardschool.com/", False),
        ("Doodle Bugs! Children's Learning Academy", "", False),
    ],
)
def test_is_sister_brand(norm: Normalizer, name: str, url: str, expected: bool) -> None:
    assert norm.is_sister_brand(name, url) is expected


def test_category_key_is_case_and_space_insensitive(norm: Normalizer) -> None:
    assert norm.category_key("  Day  Care Center ") == norm.category_key("day care center")
