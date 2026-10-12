"""Four-sheet executive workbook writer.

Reproduces the layout of ``Childtime_GBP_MultiBrand_Audit_Verified_Live.xlsx``
exactly (sheet names, titles, headers, palette, column-width rule) while
sourcing every cell from a :class:`core.gap_engine.SchoolAnalysis`.
"""

from collections.abc import Sequence

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from core import report_spec as spec
from core.gap_engine import GapEngine, SchoolAnalysis
from core.models import DiscoveredEntity
from core.report_spec import Styles as S


class ReportGenerator:
    """Writes the audit workbook."""

    def __init__(self, engine: GapEngine, brand_short: str = "Childtime") -> None:
        self.engine = engine
        self.brand = brand_short

    # ------------------------------------------------------------------ public
    def generate_workbook(self, analyses: Sequence[SchoolAnalysis], output_path: str) -> str:
        """Write all four sheets and return ``output_path``."""
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = spec.SHEET_SUMMARY
        self._sheet_summary(ws1, analyses)
        self._sheet_services(wb.create_sheet(spec.SHEET_SERVICES), analyses)
        self._sheet_categories(wb.create_sheet(spec.SHEET_CATEGORIES), analyses)
        self._sheet_profiles(wb.create_sheet(spec.SHEET_PROFILES), analyses)
        for ws in wb.worksheets:
            self._autosize(ws)
        wb.save(output_path)
        return output_path

    # ------------------------------------------------------------- scaffolding
    @staticmethod
    def _head(
        ws: Worksheet, title: str, subtitle: str, headers: Sequence[str], fill: PatternFill
    ) -> None:
        ws.sheet_view.showGridLines = True
        ws.cell(row=1, column=1, value=title).font = S.font_title
        ws.cell(row=2, column=1, value=subtitle).font = S.font_subtitle
        ws.append([])
        ws.append(list(headers))
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=spec.HEADER_ROW, column=col)
            cell.fill = fill
            cell.font = S.font_header
            cell.alignment = S.center

    @staticmethod
    def _write_row(
        ws: Worksheet,
        values: Sequence[object],
        centered: set[int],
        font: Font = S.font_regular,
        fill: PatternFill | None = None,
    ) -> int:
        ws.append(list(values))
        row = ws.max_row
        for col in range(1, len(values) + 1):
            cell = ws.cell(row=row, column=col)
            cell.font = font
            cell.border = S.thin_border
            cell.alignment = S.center if col in centered else S.left
            if fill is not None:
                cell.fill = fill
        return row

    @staticmethod
    def _style(ws: Worksheet, row: int, col: int, fill: PatternFill | None, font: Font) -> None:
        cell = ws.cell(row=row, column=col)
        if fill is not None:
            cell.fill = fill
        cell.font = font

    @staticmethod
    def _autosize(ws: Worksheet) -> None:
        for column in ws.columns:
            letter = get_column_letter(column[0].column)
            longest = 0
            for cell in column:
                if cell.row > 2 and cell.value is not None and str(cell.value):
                    longest = max(longest, len(str(cell.value)))
            ws.column_dimensions[letter].width = min(max(longest + 3, 12), 52)

    @staticmethod
    def _join_or_none(items: Sequence[str]) -> str:
        return spec.LIST_SEP.join(items) if items else spec.NONE_LABEL

    # ------------------------------------------------------- sheet 1: summary
    def _sheet_summary(self, ws: Worksheet, analyses: Sequence[SchoolAnalysis]) -> None:
        self._head(
            ws,
            f"RankUno GBP Intelligence - {self.brand} Competitive Audit (100% Verified Live Data)",
            "Executive Overview: Website vs GBP Internal Sync, True Competitor Benchmarks, "
            "and Local Reputation Health",
            spec.HEADERS_SUMMARY,
            S.navy_fill,
        )
        for a in analyses:
            c = a.client
            rep = a.reputation
            internal = [r.service for r in self.engine.by_priority(a.internal_sync_gaps)]
            external = [r.gap_label for r in self.engine.by_priority(a.external_gaps)]
            cats = [r.gap_label for r in a.category_gaps]
            values = [
                c.school_id,
                c.brand,
                c.school_name,
                c.address,
                f"{c.rating}* ({c.reviews_count})",
                a.total_true,
                len(a.website_programs),
                len(a.gbp_services),
                self._join_or_none(internal),
                self._join_or_none(external),
                self._join_or_none(cats),
                rep.label if rep else "",
                a.action_plan,
            ]
            row = self._write_row(ws, values, centered={1, 5, 6, 7, 8})
            self._style(ws, row, 9, S.soft_red_fill, S.font_alert)
            self._style(ws, row, 10, S.soft_red_fill, S.font_alert)
            if rep is not None and rep.tier == "CRITICAL":
                self._style(ws, row, 12, S.soft_red_fill, S.font_alert)

    # ------------------------------------------------------ sheet 2: services
    def _sheet_services(self, ws: Worksheet, analyses: Sequence[SchoolAnalysis]) -> None:
        groups: list[str] = []
        for a in analyses:
            for comp in a.true_competitors:
                if comp.brand_group not in groups:
                    groups.append(comp.brand_group)
        self._head(
            ws,
            f"Granular Program & Service Matrix: {self.brand} vs Verified Real Competitors",
            f"Benchmarked against real nearby schools ({', '.join(groups)})",
            spec.HEADERS_SERVICES,
            S.dark_teal_fill,
        )
        for a in analyses:
            for r in a.service_rows:
                values = [
                    a.client.school_name,
                    r.service,
                    r.website_label,
                    r.gbp_label,
                    r.pct_label,
                    r.count_label,
                    r.finding,
                ]
                row = self._write_row(ws, values, centered={3, 4, 5, 6})
                self._style(ws, row, 4, *self._service_style(r.tier))

    @staticmethod
    def _service_style(tier: str) -> tuple[PatternFill, Font]:
        colour = spec.SERVICE_TIER_FILL[tier]
        fnt = {
            "CRITICAL": S.font_alert,
            "MARKET": S.font_alert,
            "INTERNAL": S.font_bold,
            "DEFEND": S.font_ok,
            "USP": S.font_ok,
            "MONITOR": S.font_regular,
        }[tier]
        return spec.fill(colour), fnt

    # ---------------------------------------------------- sheet 3: categories
    def _sheet_categories(self, ws: Worksheet, analyses: Sequence[SchoolAnalysis]) -> None:
        self._head(
            ws,
            "Google Business Profile Category Alignment & Market Adoption",
            "Analyzes Primary and Secondary Google Categories among verified local competitors",
            spec.HEADERS_CATEGORIES,
            S.navy_fill,
        )
        for a in analyses:
            c = a.client
            for r in a.category_rows:
                values = [
                    c.school_name,
                    c.primary_category,
                    spec.LIST_SEP.join(c.additional_categories),
                    r.category,
                    r.rate_label,
                    spec.GOOGLE_CLASSIFICATION,
                    r.recommendation,
                ]
                row = self._write_row(ws, values, centered={2, 5, 6})
                fnt = {"CRITICAL": S.font_alert, "CONSIDER": S.font_bold, "COVERED": S.font_ok}[
                    r.tier
                ]
                self._style(ws, row, 7, spec.fill(spec.CATEGORY_TIER_FILL[r.tier]), fnt)

    # ------------------------------------------------------ sheet 4: profiles
    def _sheet_profiles(self, ws: Worksheet, analyses: Sequence[SchoolAnalysis]) -> None:
        self._head(
            ws,
            "Master Profile Inventory: 100% Verified Live Business Profiles",
            "Verified live school addresses, Google Maps links, ratings, review counts, "
            "categories, and programs",
            spec.HEADERS_PROFILES,
            S.navy_fill,
        )
        centered = {1, 7, 8, 9}
        for a in analyses:
            c = a.client
            client_row = [
                spec.CLASSIFICATION_CLIENT,
                c.school_name,
                c.school_name,
                c.website_url,
                c.maps_url,
                c.address,
                "0.0",
                str(c.rating),
                str(c.reviews_count),
                c.primary_category,
                spec.LIST_SEP.join(c.all_categories),
                spec.PROGRAM_SEP.join(a.website_programs),
            ]
            self._write_row(ws, client_row, centered, font=S.font_bold, fill=S.client_blue_fill)
            for ent in [*a.true_competitors, *a.sister_brands]:
                self._write_entity(ws, a, ent, centered)

    def _write_entity(
        self, ws: Worksheet, a: SchoolAnalysis, ent: DiscoveredEntity, centered: set[int]
    ) -> None:
        is_sister = ent.classification == spec.CLASSIFICATION_SISTER
        values = [
            ent.classification or spec.CLASSIFICATION_TRUE,
            a.client.school_name,
            ent.name,
            ent.website_url,
            ent.maps_url,
            ent.address,
            str(ent.distance_miles),
            str(ent.rating),
            str(ent.reviews_count),
            ent.primary_category,
            spec.LIST_SEP.join(ent.all_categories),
            spec.PROGRAM_SEP.join(ent.services),
        ]
        self._write_row(
            ws,
            values,
            centered,
            font=S.font_muted if is_sister else S.font_regular,
            fill=S.sister_fill if is_sister else None,
        )
