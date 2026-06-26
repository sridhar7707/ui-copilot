"""
Tests for html_analyzer.parse() against the hand-written sample HTML files.
Each test asserts a specific ParsedPage field rather than the full dict,
so failures are precise about what the parser got wrong.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from backend.analyzers.html_analyzer import parse

_SAMPLES = Path(__file__).parent.parent / "samples"
BAD_HTML = (_SAMPLES / "bad_ui.html").read_text(encoding="utf-8")
GOOD_HTML = (_SAMPLES / "good_ui.html").read_text(encoding="utf-8")


class TestBadUiTypography:
    def test_body_font_size(self):
        assert parse(BAD_HTML)["body_font_size_px"] == 11.0

    def test_font_count_exceeds_limit(self):
        fonts = parse(BAD_HTML)["fonts"]
        assert len(fonts) >= 4, f"Expected ≥4 fonts, got {fonts}"

    def test_line_height_tight(self):
        lh = parse(BAD_HTML)["line_height"]
        assert lh is not None and lh <= 1.2

    def test_h1_size(self):
        headings = parse(BAD_HTML)["headings"]
        h1 = next((h for h in headings if h["level"] == 1), None)
        assert h1 is not None and h1["font_size_px"] == 20.0

    def test_h2_size(self):
        headings = parse(BAD_HTML)["headings"]
        h2 = next((h for h in headings if h["level"] == 2), None)
        assert h2 is not None and h2["font_size_px"] == 18.0

    def test_heading_hierarchy_weak(self):
        headings = parse(BAD_HTML)["headings"]
        h1 = next((h for h in headings if h["level"] == 1), None)
        h2 = next((h for h in headings if h["level"] == 2), None)
        assert h1 and h2
        assert (h1["font_size_px"] / h2["font_size_px"]) < 1.2


class TestBadUiButtons:
    def test_button_count(self):
        btns = parse(BAD_HTML)["buttons"]
        assert len(btns) >= 3, f"Expected ≥3 buttons, got {len(btns)}"

    def test_button_padding_small(self):
        btns = parse(BAD_HTML)["buttons"]
        button_tags = [b for b in btns if b["text"] in ("Submit", "Cancel", "Delete")]
        assert all(b["padding_top_px"] <= 3.0 for b in button_tags)
        assert all(b["padding_left_px"] <= 6.0 for b in button_tags)

    def test_button_height_small(self):
        btns = parse(BAD_HTML)["buttons"]
        button_tags = [b for b in btns if b["text"] in ("Submit", "Cancel", "Delete")]
        assert all(b["height_px"] < 44.0 for b in button_tags)

    def test_no_focus_styles(self):
        btns = parse(BAD_HTML)["buttons"]
        assert all(not b["has_focus_style"] for b in btns)

    def test_distinct_backgrounds(self):
        btns = parse(BAD_HTML)["buttons"]
        # 3 <button> elements have 3 different background colours
        named_btns = [b for b in btns if b["text"] in ("Submit", "Cancel", "Delete")]
        colors = {b["background_color"] for b in named_btns}
        assert len(colors) == 3


class TestBadUiForms:
    def test_inputs_have_no_labels(self):
        inputs = [i for i in parse(BAD_HTML)["inputs"] if i["input_type"] not in ("submit",)]
        assert len(inputs) >= 3
        assert all(not i["has_label"] for i in inputs)

    def test_inputs_use_placeholder_as_label(self):
        inputs = [i for i in parse(BAD_HTML)["inputs"] if i["input_type"] not in ("submit",)]
        with_placeholder = [i for i in inputs if i["placeholder"]]
        assert len(with_placeholder) >= 2


class TestBadUiTable:
    def test_table_has_no_header(self):
        tables = parse(BAD_HTML)["tables"]
        assert len(tables) == 1
        assert not tables[0]["has_header"]

    def test_cell_padding_small(self):
        tables = parse(BAD_HTML)["tables"]
        assert tables[0]["cell_padding_px"] <= 3.0


class TestBadUiCards:
    def test_card_padding_small(self):
        cards = parse(BAD_HTML)["cards"]
        assert len(cards) >= 1
        assert all(c["padding_top_px"] <= 6.0 for c in cards)


class TestBadUiKpi:
    def test_kpi_count_high(self):
        assert parse(BAD_HTML)["kpi_card_count"] == 12


class TestBadUiWhitespace:
    def test_whitespace_ratio_low(self):
        ratio = parse(BAD_HTML)["whitespace_ratio"]
        assert ratio < 0.20, f"Expected low whitespace ratio, got {ratio:.3f}"


class TestBadUiSpacing:
    def test_spacing_values_off_grid(self):
        values = parse(BAD_HTML)["spacing_values_px"]
        off_grid = [v for v in values if v > 0 and v % 8 > 0.5 and (8 - v % 8) > 0.5]
        assert len(off_grid) > 2, f"Expected >2 off-grid values, got {off_grid}"


class TestGoodUiTypography:
    def test_body_font_size(self):
        assert parse(GOOD_HTML)["body_font_size_px"] == 16.0

    def test_font_count_within_limit(self):
        fonts = parse(GOOD_HTML)["fonts"]
        assert len(fonts) <= 2, f"Expected ≤2 fonts, got {fonts}"

    def test_line_height_comfortable(self):
        lh = parse(GOOD_HTML)["line_height"]
        assert lh is not None and lh >= 1.4

    def test_h1_size(self):
        headings = parse(GOOD_HTML)["headings"]
        h1 = next((h for h in headings if h["level"] == 1), None)
        assert h1 is not None and h1["font_size_px"] == 32.0

    def test_h2_size(self):
        headings = parse(GOOD_HTML)["headings"]
        h2 = next((h for h in headings if h["level"] == 2), None)
        assert h2 is not None and h2["font_size_px"] == 24.0

    def test_heading_hierarchy_strong(self):
        headings = parse(GOOD_HTML)["headings"]
        h1 = next((h for h in headings if h["level"] == 1), None)
        h2 = next((h for h in headings if h["level"] == 2), None)
        assert h1 and h2
        assert (h1["font_size_px"] / h2["font_size_px"]) >= 1.2


class TestGoodUiButtons:
    def test_buttons_have_focus_style(self):
        btns = parse(GOOD_HTML)["buttons"]
        assert len(btns) >= 2
        assert all(b["has_focus_style"] for b in btns)

    def test_button_height_adequate(self):
        btns = parse(GOOD_HTML)["buttons"]
        assert all(b["height_px"] >= 44.0 for b in btns)

    def test_button_padding_adequate(self):
        btns = parse(GOOD_HTML)["buttons"]
        assert all(b["padding_top_px"] >= 6.0 for b in btns)
        assert all(b["padding_left_px"] >= 12.0 for b in btns)


class TestGoodUiForms:
    def test_inputs_have_labels(self):
        inputs = parse(GOOD_HTML)["inputs"]
        assert len(inputs) >= 3
        assert all(i["has_label"] for i in inputs), (
            f"Inputs missing labels: {[i for i in inputs if not i['has_label']]}"
        )

    def test_input_focus_styles(self):
        inputs = parse(GOOD_HTML)["inputs"]
        assert all(i["has_focus_style"] for i in inputs)


class TestGoodUiTable:
    def test_table_has_header(self):
        tables = parse(GOOD_HTML)["tables"]
        assert len(tables) == 1
        assert tables[0]["has_header"]

    def test_table_has_zebra(self):
        tables = parse(GOOD_HTML)["tables"]
        assert tables[0]["has_zebra_striping"]

    def test_cell_padding_adequate(self):
        tables = parse(GOOD_HTML)["tables"]
        assert tables[0]["cell_padding_px"] >= 8.0


class TestGoodUiCards:
    def test_card_padding_adequate(self):
        cards = parse(GOOD_HTML)["cards"]
        assert len(cards) >= 1
        assert all(c["padding_top_px"] >= 16.0 for c in cards)


class TestGoodUiKpi:
    def test_kpi_count_low(self):
        assert parse(GOOD_HTML)["kpi_card_count"] == 4


class TestGoodUiWhitespace:
    def test_whitespace_ratio_adequate(self):
        ratio = parse(GOOD_HTML)["whitespace_ratio"]
        assert ratio >= 0.20, f"Expected whitespace ≥0.20, got {ratio:.3f}"
