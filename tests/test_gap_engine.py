from core.gap_engine import GapEngine, SchoolAnalysis
from core.models import AuditDataset, SchoolAudit


def _row(a: SchoolAnalysis, service: str):
    return next(r for r in a.service_rows if r.service == service)


def test_sister_brand_is_excluded_from_denominator(engine: GapEngine, small_audit: SchoolAudit) -> None:
    a = engine.analyze(small_audit)
    assert a.total_true == 3
    assert [s.name for s in a.sister_brands] == ["La Petite Academy of Testville"]
    assert all(s.classification == "SISTER BRAND (FILTERED)" for s in a.sister_brands)
    assert all(c.classification == "TRUE COMPETITOR" for c in a.true_competitors)
    # Grow Fit is offered only by the sister brand -> 0 of 3, not 1 of 4
    assert _row(a, "Grow Fit").count_label == "0 of 3 competitors"


def test_every_service_tier_is_reachable(engine: GapEngine, small_audit: SchoolAudit) -> None:
    a = engine.analyze(small_audit)
    tiers = {r.service: r.tier for r in a.service_rows}
    assert tiers == {
        "Infant Care": "DEFEND",
        "Preschool Program": "CRITICAL",
        "Summer Camp": "CRITICAL",
        "Grow Fit": "INTERNAL",
        "Pre-K": "MARKET",
        "Private Kindergarten": "MONITOR",
        "Toddler Care": "MONITOR",
    }
    assert _row(a, "Summer Camp").pct == 67
    assert _row(a, "Pre-K").count_label == "2 of 3 competitors"


def test_usp_tier(engine: GapEngine, small_audit: SchoolAudit) -> None:
    client = small_audit.client.model_copy(update={"gbp_services": ["Infant Care", "Drop-In Care"]})
    a = engine.analyze(small_audit.model_copy(update={"client": client}))
    assert _row(a, "Drop-In Care").tier == "USP"
    assert _row(a, "Drop-In Care").finding.startswith("DIFFERENTIATOR (USP): Childtime")


def test_gap_views_are_consistent_with_rows(engine: GapEngine, small_audit: SchoolAudit) -> None:
    a = engine.analyze(small_audit)
    assert {r.service for r in a.internal_sync_gaps} == {
        r.service for r in a.service_rows if r.offered_website and not r.claimed_gbp
    }
    assert {r.service for r in a.external_gaps} == {
        r.service for r in a.service_rows if not r.claimed_gbp and r.pct >= engine.threshold
    }
    assert {r.service for r in a.external_gaps} == {"Preschool Program", "Summer Camp", "Pre-K"}
    assert a.gbp_claimed_count == sum(1 for r in a.service_rows if r.claimed_gbp) == 1


def test_percentages_are_half_up_everywhere(engine: GapEngine, pilot_dataset: AuditDataset) -> None:
    for audit in pilot_dataset.schools:
        a = engine.analyze(audit)
        for r in a.service_rows:
            assert r.pct == engine.normalizer.pct(r.comp_count, r.comp_total)
            assert r.comp_total == a.total_true
            assert r.comp_count == len(r.competitors)
        for c in a.category_rows:
            assert c.pct == engine.normalizer.pct(c.count, c.total)
            assert c.total == a.total_true


def test_category_tiers(engine: GapEngine, small_audit: SchoolAudit) -> None:
    a = engine.analyze(small_audit)
    by_name = {c.category: c for c in a.category_rows}
    assert by_name["Day care center"].tier == "COVERED"
    assert by_name["Preschool"].tier == "COVERED"
    assert by_name["Child care agency"].rate_label == "2 of 3 (67%)"
    assert by_name["Child care agency"].tier == "CRITICAL"
    assert [c.gap_label for c in a.category_gaps] == ["Child care agency (67% comps)"]
    # sorted by adoption, highest first
    assert [c.count for c in a.category_rows] == sorted((c.count for c in a.category_rows), reverse=True)


def test_reputation_and_action_plan(engine: GapEngine, small_audit: SchoolAudit) -> None:
    low = small_audit.client.model_copy(update={"rating": 3.6, "reviews_count": 9})
    a = engine.analyze(small_audit.model_copy(update={"client": low}))
    assert a.reputation is not None
    assert a.reputation.tier == "CRITICAL"
    assert a.reputation.label == "CRITICAL: 3.6 Stars (9 revs) (Lagging behind Beta 4.9*)"
    assert a.action_plan == (
        "1. Immediately publish Preschool Program & Summer Camp as GBP service chips "
        "(live on the school website; claimed by 67%+ of true competitors). "
        "2. Publish remaining website programs as GBP service chips: Grow Fit. "
        "3. Evaluate adding Pre-K (claimed by 50%+ of competitors but not offered on the "
        "website or GBP). "
        "4. Add Child care agency as a secondary GBP category (67% of true competitors claim it). "
        "5. Launch a proactive review-generation campaign to lift the 3.6* rating above Beta (4.9*)."
    )

    healthy = engine.analyze(small_audit)
    assert healthy.reputation is not None
    assert healthy.reputation.label == "HEALTHY: 4.5 Stars (20 revs)"
    assert "review-generation" not in healthy.action_plan


def test_action_plan_when_nothing_to_do(engine: GapEngine, small_audit: SchoolAudit) -> None:
    client = small_audit.client.model_copy(
        update={
            "website_programs": ["Infants"],
            "gbp_services": ["Infant Care", "Preschool", "Summer Camp", "Pre-K"],
            "additional_categories": ["Preschool", "Child care agency"],
        }
    )
    a = engine.analyze(small_audit.model_copy(update={"client": client}))
    assert a.action_plan == "1. Maintain review velocity and keep GBP services in sync with the website."


def test_by_priority_orders_by_adoption_then_taxonomy(engine: GapEngine, small_audit: SchoolAudit) -> None:
    a = engine.analyze(small_audit)
    ordered = [r.service for r in engine.by_priority(a.internal_sync_gaps)]
    assert ordered == ["Preschool Program", "Summer Camp", "Grow Fit"]


def test_pilot_dataset_expectations(engine: GapEngine, pilot_dataset: AuditDataset) -> None:
    fairport, henrietta = (engine.analyze(s) for s in pilot_dataset.schools)
    assert fairport.total_true == 6 and len(fairport.sister_brands) == 1
    assert henrietta.total_true == 5 and len(henrietta.sister_brands) == 1
    assert [r.gap_label for r in engine.by_priority(fairport.external_gaps)] == [
        "Preschool Program (100% comps)",
        "Summer Camp (83% comps)",
    ]
    assert [c.gap_label for c in henrietta.category_gaps] == ["Child care agency (80% comps)"]
    assert henrietta.reputation is not None
    assert henrietta.reputation.label == "CRITICAL: 3.7 Stars (16 revs) (Lagging behind Doodle Bugs! 4.8*)"
    assert _row(fairport, "Before and After School").claimed_gbp is True
    assert _row(fairport, "Summer Camp").count_label == "5 of 6 competitors"
