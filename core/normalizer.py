"""Normalisation helpers shared by the engine, reporter and validator.

Covers service-taxonomy mapping, sister-brand detection, category keys and
exact (half-up) percentage rounding.
"""

from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

from config import settings
from core.taxonomy import CORE_PROGRAMS, SERVICE_SYNONYMS


class Normalizer:
    """Stateless mapping rules; one instance is shared across a run."""

    def __init__(self, sister_brands: Iterable[str] | None = None) -> None:
        if sister_brands is None:
            names = list(settings.LCG_SISTER_BRANDS) + list(settings.LCG_SISTER_ALIASES)
        else:
            names = list(sister_brands)
        self.sister_tokens: tuple[str, ...] = tuple(
            sorted({n.strip().lower() for n in names if n.strip()})
        )
        self._order: dict[str, int] = {name: i for i, name in enumerate(CORE_PROGRAMS)}

    # ------------------------------------------------------------------ services
    @staticmethod
    def _key(raw: str) -> str:
        return " ".join(raw.strip().lower().split())

    def canonical_service(self, raw: str) -> str | None:
        """Map a raw service label onto a canonical program, or ``None``."""
        key = self._key(raw)
        if not key:
            return None
        if key in SERVICE_SYNONYMS:
            return SERVICE_SYNONYMS[key]
        alt = " ".join(key.replace("&", "and").split())
        return SERVICE_SYNONYMS.get(alt)

    def canonical_set(self, raw_services: Iterable[str]) -> dict[str, str]:
        """Return ``{canonical: first raw label}`` for every mapped service."""
        out: dict[str, str] = {}
        for raw in raw_services:
            canon = self.canonical_service(raw)
            if canon and canon not in out:
                out[canon] = raw.strip()
        return out

    def unmapped(self, raw_services: Iterable[str]) -> list[str]:
        """Raw labels that do not map onto the taxonomy."""
        return [r.strip() for r in raw_services if self.canonical_service(r) is None]

    def taxonomy_rank(self, canonical: str) -> int:
        """Position of a canonical program in the display order."""
        return self._order.get(canonical, len(self._order))

    def order_raw_programs(self, raw_programs: Iterable[str]) -> list[str]:
        """Order raw labels by taxonomy rank; unmapped labels go last (A-Z)."""
        mapped: list[tuple[int, str]] = []
        unmapped: list[str] = []
        for raw in raw_programs:
            canon = self.canonical_service(raw)
            if canon:
                mapped.append((self.taxonomy_rank(canon), raw.strip()))
            else:
                unmapped.append(raw.strip())
        mapped.sort(key=lambda t: t[0])
        return [r for _, r in mapped] + sorted(unmapped, key=str.lower)

    # ---------------------------------------------------------------- categories
    @staticmethod
    def category_key(raw: str) -> str:
        """Case/whitespace-insensitive comparison key for a GBP category."""
        return " ".join(raw.strip().lower().split())

    # -------------------------------------------------------------- sister brand
    def is_sister_brand(self, business_name: str, domain_or_url: str = "") -> bool:
        """True when the name or URL contains any Learning Care Group brand."""
        haystack = f"{business_name} {domain_or_url}".lower()
        return any(token in haystack for token in self.sister_tokens)

    # ------------------------------------------------------------------ maths
    @staticmethod
    def pct(count: int, total: int) -> int:
        """Whole-number percentage with exact half-up rounding (2/3 -> 67)."""
        if total <= 0:
            return 0
        value = Decimal(count) * Decimal(100) / Decimal(total)
        return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
