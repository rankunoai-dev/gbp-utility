"""Gap & benchmark engine.

Produces ONE :class:`SchoolAnalysis` per client school. Every number and
label that appears on any sheet of the workbook is computed here, once, so
the Executive Summary, Service Comparison Matrix, Category Gap Matrix and
Raw Profile Details can never disagree with each other.
"""

from dataclasses import dataclass, field
from typing import Literal

from config import settings
from core.models import ClientSchool, DiscoveredEntity, SchoolAudit
from core.normalizer import Normalizer
from core.taxonomy import CORE_PROGRAMS

ServiceTier = Literal["CRITICAL", "INTERNAL", "MARKET", "DEFEND", "USP", "MONITOR"]
CategoryTier = Literal["CRITICAL", "CONSIDER", "COVERED"]
ReputationTier = Literal["CRITICAL", "HEALTHY"]

GBP_YES = "YES"
GBP_MISSING = "NO (MISSING ON GBP)"


@dataclass(frozen=True)
class ServiceRow:
    """One canonical program benchmarked for one client school."""

    service: str
    offered_website: bool
    claimed_gbp: bool
    comp_count: int
    comp_total: int
    pct: int
    competitors: tuple[str, ...]
    tier: ServiceTier
    finding: str

    @property
    def gbp_label(self) -> str:
        return GBP_YES if self.claimed_gbp else GBP_MISSING

    @property
    def website_label(self) -> str:
        return "YES" if self.offered_website else "NO"

    @property
    def pct_label(self) -> str:
        return f"{self.pct}%"

    @property
    def count_label(self) -> str:
        return f"{self.comp_count} of {self.comp_total} competitors"

    @property
    def gap_label(self) -> str:
        return f"{self.service} ({self.pct}% comps)"


@dataclass(frozen=True)
class CategoryRow:
    """One Google category discovered among true competitors."""

    category: str
    count: int
    total: int
    pct: int
    covered: bool
    tier: CategoryTier
    recommendation: str

    @property
    def rate_label(self) -> str:
        return f"{self.count} of {self.total} ({self.pct}%)"

    @property
    def gap_label(self) -> str:
        return f"{self.category} ({self.pct}% comps)"


@dataclass(frozen=True)
class Reputation:
    """Local reputation health for the client school."""

    rating: float
    reviews: int
    tier: ReputationTier
    top_competitor: DiscoveredEntity | None
    label: str


@dataclass
class SchoolAnalysis:
    """Complete, internally consistent result for one client school."""

    client: ClientSchool
    true_competitors: list[DiscoveredEntity]
    sister_brands: list[DiscoveredEntity]
    website_programs: list[str]
    gbp_services: list[str]
    service_rows: list[ServiceRow] = field(default_factory=list)
    category_rows: list[CategoryRow] = field(default_factory=list)
    reputation: Reputation | None = None
    action_plan: str = ""

    # Derived views -------------------------------------------------------
    @property
    def total_true(self) -> int:
        return len(self.true_competitors)

    @property
    def internal_sync_gaps(self) -> list[ServiceRow]:
        """On the website, missing on GBP (CRITICAL + INTERNAL tiers)."""
        return [r for r in self.service_rows if r.tier in ("CRITICAL", "INTERNAL")]

    @property
    def external_gaps(self) -> list[ServiceRow]:
        """Missing on GBP and offered by >= threshold of true competitors."""
        return [r for r in self.service_rows if r.tier in ("CRITICAL", "MARKET")]

    @property
    def category_gaps(self) -> list[CategoryRow]:
        return [r for r in self.category_rows if r.tier == "CRITICAL"]

    @property
    def gbp_claimed_count(self) -> int:
        return sum(1 for r in self.service_rows if r.claimed_gbp)


class GapEngine:
    """Computes :class:`SchoolAnalysis` objects from validated audit input."""

    def __init__(
        self,
        normalizer: Normalizer | None = None,
        threshold_pct: int | None = None,
        reputation_floor: float | None = None,
        brand_short: str = "Childtime",
    ) -> None:
        self.normalizer = normalizer or Normalizer()
        self.threshold = settings.GAP_THRESHOLD_PCT if threshold_pct is None else threshold_pct
        self.rep_floor = (
            settings.REPUTATION_CRITICAL_BELOW if reputation_floor is None else reputation_floor
        )
        self.brand = brand_short

    # ------------------------------------------------------------------ public
    def analyze(self, audit: SchoolAudit) -> SchoolAnalysis:
        """Run the full pipeline for one school."""
        client = audit.client
        true_comps, sisters = self._partition(audit.discovered_entities)
        norm = self.normalizer

        analysis = SchoolAnalysis(
            client=client,
            true_competitors=true_comps,
            sister_brands=sisters,
            website_programs=norm.order_raw_programs(client.website_programs),
            gbp_services=norm.order_raw_programs(client.gbp_services),
        )
        analysis.service_rows = self._service_rows(client, true_comps)
        analysis.category_rows = self._category_rows(client, true_comps)
        analysis.reputation = self._reputation(client, true_comps)
        analysis.action_plan = self._action_plan(analysis)
        return analysis

    # --------------------------------------------------------------- partition
    def _partition(
        self, entities: list[DiscoveredEntity]
    ) -> tuple[list[DiscoveredEntity], list[DiscoveredEntity]]:
        true_comps: list[DiscoveredEntity] = []
        sisters: list[DiscoveredEntity] = []
        for ent in entities:
            is_sister = self.normalizer.is_sister_brand(ent.name, ent.website_url)
            label = "SISTER BRAND (FILTERED)" if is_sister else "TRUE COMPETITOR"
            tagged = ent.model_copy(update={"classification": label})
            (sisters if is_sister else true_comps).append(tagged)
        return true_comps, sisters

    # ---------------------------------------------------------------- services
    def _service_rows(
        self, client: ClientSchool, comps: list[DiscoveredEntity]
    ) -> list[ServiceRow]:
        norm = self.normalizer
        web = norm.canonical_set(client.website_programs)
        gbp = norm.canonical_set(client.gbp_services)
        offering: dict[str, list[str]] = {}
        for comp in comps:
            for canon in norm.canonical_set(comp.services):
                offering.setdefault(canon, []).append(comp.name)

        total = len(comps)
        rows: list[ServiceRow] = []
        for svc in CORE_PROGRAMS:
            on_web, on_gbp = svc in web, svc in gbp
            names = tuple(offering.get(svc, []))
            if not (on_web or on_gbp or names):
                continue
            count = len(names)
            pct = norm.pct(count, total)
            tier = self._service_tier(on_web, on_gbp, count, pct)
            rows.append(
                ServiceRow(
                    service=svc,
                    offered_website=on_web,
                    claimed_gbp=on_gbp,
                    comp_count=count,
                    comp_total=total,
                    pct=pct,
                    competitors=names,
                    tier=tier,
                    finding=self.service_finding(tier),
                )
            )
        rows.sort(key=lambda r: r.service.lower())
        return rows

    def _service_tier(self, on_web: bool, on_gbp: bool, count: int, pct: int) -> ServiceTier:
        if on_web and not on_gbp and pct >= self.threshold:
            return "CRITICAL"
        if on_web and not on_gbp:
            return "INTERNAL"
        if not on_web and not on_gbp and pct >= self.threshold:
            return "MARKET"
        if on_gbp and pct >= self.threshold:
            return "DEFEND"
        if on_gbp and count == 0:
            return "USP"
        return "MONITOR"

    def service_finding(self, tier: ServiceTier) -> str:
        """Human-readable finding for a service tier."""
        b = self.brand
        texts: dict[ServiceTier, str] = {
            "CRITICAL": (
                "CRITICAL SYNC GAP: School offers on site & competitors dominate "
                f"Google, but {b} GBP is missing chip!"
            ),
            "INTERNAL": (
                "INTERNAL SYNC GAP: School offers on website, but GBP dashboard "
                "has not published the service chip."
            ),
            "MARKET": (
                "MARKET GAP: Competitors dominate Google, but the program is not "
                "offered on the website or GBP."
            ),
            "DEFEND": "DEFEND: Active on GBP and competitive in market. Maintain review volume.",
            "USP": (
                f"DIFFERENTIATOR (USP): {b} offers & highlights on GBP; "
                "competitors in zip code omit."
            ),
            "MONITOR": "MONITOR: Niche offering in territory.",
        }
        return texts[tier]

    # -------------------------------------------------------------- categories
    def _category_rows(
        self, client: ClientSchool, comps: list[DiscoveredEntity]
    ) -> list[CategoryRow]:
        norm = self.normalizer
        client_keys = {norm.category_key(c) for c in client.all_categories}
        counts: dict[str, int] = {}
        display: dict[str, str] = {}
        for comp in comps:
            seen: set[str] = set()
            for cat in comp.all_categories:
                key = norm.category_key(cat)
                if not key or key in seen:
                    continue
                seen.add(key)
                counts[key] = counts.get(key, 0) + 1
                display.setdefault(key, cat.strip())

        total = len(comps)
        rows: list[CategoryRow] = []
        for key, count in counts.items():
            pct = norm.pct(count, total)
            covered = key in client_keys
            tier = self._category_tier(covered, pct)
            rows.append(
                CategoryRow(
                    category=display[key],
                    count=count,
                    total=total,
                    pct=pct,
                    covered=covered,
                    tier=tier,
                    recommendation=self.category_recommendation(tier),
                )
            )
        rows.sort(key=lambda r: -r.count)  # stable: ties keep discovery order
        return rows

    def _category_tier(self, covered: bool, pct: int) -> CategoryTier:
        if covered:
            return "COVERED"
        return "CRITICAL" if pct >= self.threshold else "CONSIDER"

    def category_recommendation(self, tier: CategoryTier) -> str:
        """Human-readable recommendation for a category tier."""
        texts: dict[CategoryTier, str] = {
            "CRITICAL": (
                "CRITICAL GAP: Add as Secondary Category on GBP to capture "
                "high-intent category search volume"
            ),
            "CONSIDER": (
                "CONSIDER: Seasonal addition (e.g. Summer camp category during "
                "Spring/Summer enrollment)"
            ),
            "COVERED": f"COVERED: Currently active on {self.brand} GBP profile",
        }
        return texts[tier]

    # -------------------------------------------------------------- reputation
    def _reputation(self, client: ClientSchool, comps: list[DiscoveredEntity]) -> Reputation:
        top = max(comps, key=lambda c: (c.rating, c.reviews_count), default=None)
        base = f"{client.rating} Stars ({client.reviews_count} revs)"
        if client.rating < self.rep_floor:
            label = f"CRITICAL: {base}"
            if top is not None:
                label += f" (Lagging behind {top.brand_group} {top.rating}*)"
            return Reputation(client.rating, client.reviews_count, "CRITICAL", top, label)
        return Reputation(client.rating, client.reviews_count, "HEALTHY", top, f"HEALTHY: {base}")

    # ------------------------------------------------------------- action plan
    def _action_plan(self, a: SchoolAnalysis) -> str:
        steps: list[str] = []
        critical = [r for r in a.service_rows if r.tier == "CRITICAL"]
        internal = [r for r in a.service_rows if r.tier == "INTERNAL"]
        market = [r for r in a.service_rows if r.tier == "MARKET"]

        if critical:
            names = self._join([r.service for r in self._by_priority(critical)])
            low = min(r.pct for r in critical)
            steps.append(
                f"Immediately publish {names} as GBP service chips (live on the school "
                f"website; claimed by {low}%+ of true competitors)."
            )
        if internal:
            names = self._join([r.service for r in self._by_priority(internal)])
            steps.append(f"Publish remaining website programs as GBP service chips: {names}.")
        if market:
            names = self._join([r.service for r in self._by_priority(market)])
            steps.append(
                f"Evaluate adding {names} (claimed by {self.threshold}%+ of competitors "
                "but not offered on the website or GBP)."
            )
        for cat in a.category_gaps:
            steps.append(
                f"Add {cat.category} as a secondary GBP category ({cat.pct}% of true "
                "competitors claim it)."
            )
        rep = a.reputation
        if rep is not None and rep.tier == "CRITICAL":
            target = ""
            if rep.top_competitor is not None:
                target = f" above {rep.top_competitor.brand_group} ({rep.top_competitor.rating}*)"
            steps.append(
                f"Launch a proactive review-generation campaign to lift the {rep.rating}* "
                f"rating{target}."
            )
        if not steps:
            steps.append("Maintain review velocity and keep GBP services in sync with the website.")
        return " ".join(f"{i}. {s}" for i, s in enumerate(steps, start=1))

    # ------------------------------------------------------------------ utils
    def _by_priority(self, rows: list[ServiceRow]) -> list[ServiceRow]:
        """Highest competitor adoption first, then taxonomy order."""
        return sorted(rows, key=lambda r: (-r.pct, self.normalizer.taxonomy_rank(r.service)))

    def by_priority(self, rows: list[ServiceRow]) -> list[ServiceRow]:
        """Public alias used by the reporter for gap lists."""
        return self._by_priority(rows)

    @staticmethod
    def _join(names: list[str]) -> str:
        if len(names) <= 1:
            return "".join(names)
        return ", ".join(names[:-1]) + " & " + names[-1]
