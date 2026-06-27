"""
Module 15 — Mobile Analyzer tests.

All tests are deterministic: no DB, no network.
"""
from __future__ import annotations

from backend.analyzers import mobile_analyzer
from backend.utils.config_loader import load_scoring_config

_CFG = load_scoring_config()["thresholds"]


# ── helpers ───────────────────────────────────────────────────────────────────

def _page(**kwargs) -> dict:
    defaults = {
        "buttons": [],
        "tables": [],
        "cards": [],
        "body_font_size_px": 16.0,
        "has_viewport_meta": True,
        "has_horizontal_overflow": False,
    }
    defaults.update(kwargs)
    return defaults


def _btn(pt: float = 10, pb: float = 10, fs: float = 16) -> dict:
    return {"padding_top_px": pt, "padding_bottom_px": pb, "font_size_px": fs}


def _table(cols: int) -> dict:
    return {"column_count": cols, "row_count": 5, "has_header": True}


def _card(width_px: float | None = None) -> dict:
    d: dict = {"padding_px": 16}
    if width_px is not None:
        d["width_px"] = width_px
    return d


def _ids(issues) -> set[str]:
    return {i.rule_id for i in issues}


# ── MB1 — missing viewport meta ───────────────────────────────────────────────

class TestMB1ViewportMeta:
    def test_no_viewport_meta_fires(self):
        assert "MB1_missing_viewport_meta" in _ids(
            mobile_analyzer.analyze(_page(has_viewport_meta=False), _CFG))

    def test_viewport_meta_present_no_issue(self):
        assert "MB1_missing_viewport_meta" not in _ids(
            mobile_analyzer.analyze(_page(has_viewport_meta=True), _CFG))

    def test_viewport_meta_none_no_issue(self):
        # None means "not parsed" — don't fire without evidence
        assert "MB1_missing_viewport_meta" not in _ids(
            mobile_analyzer.analyze(_page(has_viewport_meta=None), _CFG))

    def test_critical_severity(self):
        issues = mobile_analyzer.analyze(_page(has_viewport_meta=False), _CFG)
        issue = next(i for i in issues if i.rule_id == "MB1_missing_viewport_meta")
        assert issue.severity.value == "critical"


# ── MB2 — touch targets ───────────────────────────────────────────────────────

class TestMB2TouchTargets:
    def test_large_buttons_no_issue(self):
        # pt=12, fs=16, pb=12 → height = 12 + 16*1.2 + 12 = 43.2 → < 44
        # use pt=14 → 14 + 19.2 + 14 = 47.2 ≥ 44
        page = _page(buttons=[_btn(pt=14, pb=14)])
        assert "MB2_small_touch_targets" not in _ids(mobile_analyzer.analyze(page, _CFG))

    def test_small_button_fires(self):
        # pt=2, fs=12, pb=2 → 2 + 14.4 + 2 = 18.4 < 44
        page = _page(buttons=[_btn(pt=2, pb=2, fs=12)])
        assert "MB2_small_touch_targets" in _ids(mobile_analyzer.analyze(page, _CFG))

    def test_mixed_buttons_fires_if_any_small(self):
        page = _page(buttons=[_btn(pt=14, pb=14), _btn(pt=2, pb=2, fs=12)])
        assert "MB2_small_touch_targets" in _ids(mobile_analyzer.analyze(page, _CFG))

    def test_no_buttons_no_issue(self):
        assert "MB2_small_touch_targets" not in _ids(
            mobile_analyzer.analyze(_page(), _CFG))


# ── MB3 — body font size ──────────────────────────────────────────────────────

class TestMB3BodyFont:
    def test_16px_no_issue(self):
        assert "MB3_small_body_font" not in _ids(
            mobile_analyzer.analyze(_page(body_font_size_px=16.0), _CFG))

    def test_14px_at_threshold_no_issue(self):
        assert "MB3_small_body_font" not in _ids(
            mobile_analyzer.analyze(_page(body_font_size_px=14.0), _CFG))

    def test_13px_fires(self):
        assert "MB3_small_body_font" in _ids(
            mobile_analyzer.analyze(_page(body_font_size_px=13.0), _CFG))

    def test_none_body_font_no_issue(self):
        assert "MB3_small_body_font" not in _ids(
            mobile_analyzer.analyze(_page(body_font_size_px=None), _CFG))


# ── MB4 — horizontal overflow ─────────────────────────────────────────────────

class TestMB4HorizontalOverflow:
    def test_overflow_fires(self):
        assert "MB4_horizontal_overflow" in _ids(
            mobile_analyzer.analyze(_page(has_horizontal_overflow=True), _CFG))

    def test_no_overflow_no_issue(self):
        assert "MB4_horizontal_overflow" not in _ids(
            mobile_analyzer.analyze(_page(has_horizontal_overflow=False), _CFG))

    def test_none_overflow_no_issue(self):
        assert "MB4_horizontal_overflow" not in _ids(
            mobile_analyzer.analyze(_page(has_horizontal_overflow=None), _CFG))


# ── MB5 — table overflow ──────────────────────────────────────────────────────

class TestMB5TableOverflow:
    def test_4_col_table_no_issue(self):
        assert "MB5_table_overflow_mobile" not in _ids(
            mobile_analyzer.analyze(_page(tables=[_table(4)]), _CFG))

    def test_5_col_table_fires(self):
        assert "MB5_table_overflow_mobile" in _ids(
            mobile_analyzer.analyze(_page(tables=[_table(5)]), _CFG))

    def test_multiple_wide_tables(self):
        issues = mobile_analyzer.analyze(_page(tables=[_table(6), _table(7)]), _CFG)
        issue = next(i for i in issues if i.rule_id == "MB5_table_overflow_mobile")
        assert "2" in issue.evidence


# ── MB6 — fixed width cards ───────────────────────────────────────────────────

class TestMB6FixedWidthCards:
    def test_card_without_width_no_issue(self):
        assert "MB6_fixed_width_cards" not in _ids(
            mobile_analyzer.analyze(_page(cards=[_card()]), _CFG))

    def test_narrow_fixed_card_no_issue(self):
        assert "MB6_fixed_width_cards" not in _ids(
            mobile_analyzer.analyze(_page(cards=[_card(width_px=320)]), _CFG))

    def test_wide_fixed_card_fires(self):
        assert "MB6_fixed_width_cards" in _ids(
            mobile_analyzer.analyze(_page(cards=[_card(width_px=600)]), _CFG))


# ── issue shape ───────────────────────────────────────────────────────────────

class TestIssueShape:
    def test_all_issues_have_why_and_references(self):
        page = _page(
            has_viewport_meta=False,
            body_font_size_px=12.0,
            has_horizontal_overflow=True,
            buttons=[_btn(pt=1, pb=1, fs=10)],
            tables=[_table(8)],
            cards=[_card(width_px=700)],
        )
        issues = mobile_analyzer.analyze(page, _CFG)
        assert issues
        for issue in issues:
            assert issue.why, f"{issue.rule_id} missing why"
            assert issue.references, f"{issue.rule_id} missing references"

    def test_clean_page_no_issues(self):
        page = _page(
            has_viewport_meta=True,
            body_font_size_px=16.0,
            has_horizontal_overflow=False,
            buttons=[_btn(pt=14, pb=14)],
            tables=[_table(4)],
            cards=[_card(width_px=320)],
        )
        assert mobile_analyzer.analyze(page, _CFG) == []
