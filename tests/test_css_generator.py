"""
Module 10 — CSS Generator.
"""
from __future__ import annotations

import pytest

from backend.services import css_generator, scoring_engine
from tests.fixtures import bad_page, clean_page


@pytest.fixture
def bad_css():
    return css_generator.generate(scoring_engine.analyze(bad_page()))


@pytest.fixture
def clean_css():
    return css_generator.generate(scoring_engine.analyze(clean_page()))


class TestCssStructure:
    def test_returns_string(self, bad_css):
        assert isinstance(bad_css, str)

    def test_not_empty(self, bad_css):
        assert len(bad_css) > 50

    def test_has_uicopilot_header(self, bad_css):
        assert "UICopilot" in bad_css

    def test_has_root_block(self, bad_css):
        assert ":root {" in bad_css

    def test_has_space_tokens(self, bad_css):
        assert "--space-" in bad_css

    def test_has_font_size_token(self, bad_css):
        assert "--font-size-body" in bad_css

    def test_has_button_tokens(self, bad_css):
        assert "--btn-padding-y" in bad_css

    def test_is_valid_css_structure(self, bad_css):
        open_count = bad_css.count("{")
        close_count = bad_css.count("}")
        assert open_count == close_count, "Mismatched braces"


class TestCssBadPageFixes:
    def test_typography_block_present(self, bad_css):
        assert "Typography Fixes" in bad_css

    def test_button_block_present(self, bad_css):
        assert "Button Fixes" in bad_css

    def test_focus_visible_included(self, bad_css):
        assert ":focus-visible" in bad_css

    def test_form_block_present(self, bad_css):
        assert "Form Fixes" in bad_css

    def test_table_block_present(self, bad_css):
        assert "Table Fixes" in bad_css

    def test_zebra_striping_included(self, bad_css):
        assert "nth-child(even)" in bad_css

    def test_spacing_block_present(self, bad_css):
        assert "Spacing Fixes" in bad_css


class TestCssTokenValues:
    def test_grid_scale_multiples(self, bad_css):
        # 8pt grid: space-8, space-16, space-24, space-32 should all appear
        for val in (8, 16, 24, 32):
            assert f"--space-{val}:" in bad_css

    def test_min_height_token_numeric(self, bad_css):
        assert "--btn-min-height:" in bad_css
        idx = bad_css.index("--btn-min-height:")
        snippet = bad_css[idx:idx + 30]
        assert "px" in snippet


class TestCssIsIdempotent:
    def test_same_result_same_css(self):
        result = scoring_engine.analyze(bad_page())
        assert css_generator.generate(result) == css_generator.generate(result)


class TestCssCleanPage:
    def test_clean_page_still_produces_tokens(self, clean_css):
        assert ":root {" in clean_css
        assert "--font-size-body" in clean_css

    def test_clean_page_fewer_fix_blocks(self, clean_css, bad_css):
        assert len(clean_css) < len(bad_css)
