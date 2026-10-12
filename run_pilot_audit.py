"""End-to-end pilot run: dataset -> (live website sync) -> engine -> workbook -> validation.

Usage::

    python run_pilot_audit.py                       # live website sync, default paths
    python run_pilot_audit.py --offline             # use dataset programs only
    python run_pilot_audit.py --dataset my.json --output my.xlsx
    python run_pilot_audit.py --client-source gbp-api   # client profile from the GBP API
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import settings  # noqa: E402
from core.adapters.gbp_api_adapter import GBPApiAdapter, apply_snapshot  # noqa: E402
from core.adapters.website_adapter import WebsiteAdapter  # noqa: E402
from core.dataset import load_dataset  # noqa: E402
from core.gap_engine import GapEngine, SchoolAnalysis  # noqa: E402
from core.models import AuditDataset, SchoolAudit  # noqa: E402
from core.reporter import ReportGenerator  # noqa: E402
from core.validator import format_report, validate_workbook  # noqa: E402

DEFAULT_DATASET = "data/childtime_pilot_dataset.json"
DEFAULT_OUTPUT = "RankUno_GBP_Intelligence_Audit_Master.xlsx"

log = logging.getLogger("gbp.pilot")


def sync_live_website_programs(audit: SchoolAudit, adapter: WebsiteAdapter) -> SchoolAudit:
    """Replace the dataset's website programs with the live list when reachable."""
    client = audit.client
    if not client.website_url:
        return audit
    try:
        live = adapter.scrape_school_page(client.website_url)
    except Exception as exc:  # network / parse failure -> keep verified dataset
        log.warning(
            "%s: live website fetch failed (%s); using dataset programs", client.school_name, exc
        )
        return audit
    programs = live.get("programs") or []
    if not programs:
        log.warning(
            "%s: live website returned no programs; using dataset programs", client.school_name
        )
        return audit
    before = {p.lower() for p in client.website_programs}
    after = {p.lower() for p in programs}
    if before != after:
        log.info(
            "%s: live programs differ from dataset (+%s / -%s)",
            client.school_name,
            sorted(after - before),
            sorted(before - after),
        )
    else:
        log.info(
            "%s: live website programs match the dataset (%d)", client.school_name, len(programs)
        )
    return audit.model_copy(
        update={"client": client.model_copy(update={"website_programs": programs})}
    )


def sync_gbp_profile(audit: SchoolAudit, adapter: "GBPApiAdapter") -> SchoolAudit:
    """Overlay categories, service chips, rating, reviews and address from the GBP API."""
    client = audit.client
    if not (client.gbp_account_id and client.gbp_location_id):
        raise ValueError(
            f"{client.school_name}: gbp_account_id / gbp_location_id missing in the dataset "
            "(run `python scripts/gbp_auth.py locations --account <id>` to find them)"
        )
    snap = adapter.fetch_location(client.gbp_account_id, client.gbp_location_id)
    merged = apply_snapshot(client, snap)
    log.info(
        "%s: GBP API -> %s | %s + %s | %d service items | %s* (%s)",
        client.school_name,
        snap.title,
        merged.primary_category,
        merged.additional_categories,
        len(merged.gbp_services),
        merged.rating,
        merged.reviews_count,
    )
    return audit.model_copy(update={"client": merged})


def build_gbp_adapter() -> "GBPApiAdapter":
    """Requests session + refresh-token provider from scripts/gbp_auth.py."""
    import requests

    from scripts.gbp_auth import token_provider_from_file

    return GBPApiAdapter(requests.Session(), token_provider_from_file())


def run(
    dataset: AuditDataset, output: str, offline: bool, client_source: str = "dataset"
) -> tuple[list[SchoolAnalysis], str]:
    """Execute the pipeline; return the analyses and the path actually written."""
    engine = GapEngine(brand_short=dataset.client_brand_short)
    reporter = ReportGenerator(engine, brand_short=dataset.client_brand_short)
    adapter = WebsiteAdapter()
    gbp_adapter = build_gbp_adapter() if client_source == "gbp-api" else None

    analyses: list[SchoolAnalysis] = []
    for audit in dataset.schools:
        if gbp_adapter is not None:
            audit = sync_gbp_profile(audit, gbp_adapter)
        if not offline:
            audit = sync_live_website_programs(audit, adapter)
        analysis = engine.analyze(audit)
        analyses.append(analysis)
        log.info(
            "%s: %d true competitors, %d sister brands filtered, %d internal gaps, "
            "%d external gaps, %d category gaps",
            analysis.client.school_name,
            analysis.total_true,
            len(analysis.sister_brands),
            len(analysis.internal_sync_gaps),
            len(analysis.external_gaps),
            len(analysis.category_gaps),
        )

    written = write_with_fallback(reporter, analyses, output)
    log.info("workbook written: %s", written)
    return analyses, written


def write_with_fallback(
    reporter: ReportGenerator, analyses: list[SchoolAnalysis], output: str
) -> str:
    """Save to ``output``; if Excel holds a lock on it, save next to it with a timestamp."""
    try:
        return reporter.generate_workbook(analyses, output)
    except PermissionError:
        target = Path(output)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback = target.with_name(f"{target.stem}_{stamp}{target.suffix}")
        log.warning("%s is locked (open in Excel?); writing %s instead", output, fallback.name)
        return reporter.generate_workbook(analyses, str(fallback))


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--offline", action="store_true", help="skip the live website program sync")
    parser.add_argument(
        "--no-validate", action="store_true", help="skip the post-write consistency validation"
    )
    parser.add_argument(
        "--client-source",
        choices=["dataset", "gbp-api"],
        default="dataset",
        help="where client categories/services/rating come from (gbp-api = official API)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log.info("RankUno GBP Intelligence Engine - pilot audit")

    dataset = load_dataset(args.dataset)
    _, written = run(dataset, args.output, offline=args.offline, client_source=args.client_source)

    if args.no_validate:
        return 0
    report = validate_workbook(
        written,
        threshold_pct=settings.GAP_THRESHOLD_PCT,
        rep_floor=settings.REPUTATION_CRITICAL_BELOW,
    )
    print(format_report(report))  # noqa: T201 - CLI output
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
