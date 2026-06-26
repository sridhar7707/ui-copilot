"""
Module 4 — Design System Detection.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from backend.analyzers.design_system_analyzer import analyze
from tests.fixtures import bad_page, clean_page


@pytest.fixture
def thresholds():
    cfg = json.loads(pathlib.Path("config/scoring.json").read_text())
    return cfg["thresholds"]


@pytest.fixture
def bad(thresholds):
    return analyze(bad_page(), thresholds)


@pytest.fixture
def clean(thresholds):
    return analyze(clean_page(), thresholds)


# ── DS1 — button colour palette ───────────────────────────────────────────────

class TestButtonColourPalette:
    def test_fires_on_many_colours(self, bad):
        rule_ids = [i.rule_id for i in bad]
        assert "DS1_button_color_palette" in rule_ids

    def test_not_fire_on_two_colours(self, clean):
        rule_ids = [i.rule_id for i in clean]
        assert "DS1_button_color_palette" not in rule_ids

    def test_has_why_and_refs(self, bad):
        issues = [i for i in bad if i.rule_id == "DS1_button_color_palette"]
        assert issues[0].why
        assert issues[0].references


# ── DS2 — button radius inconsistency ────────────────────────────────────────

class TestButtonRadiusInconsistency:
    def test_fires_on_bad_page(self, bad):
        # bad_page has radii 2, 12, 0
        rule_ids = [i.rule_id for i in bad]
        assert "DS2_button_radius_inconsistency" in rule_ids

    def test_not_fire_on_clean_page(self, clean):
        rule_ids = [i.rule_id for i in clean]
        assert "DS2_button_radius_inconsistency" not in rule_ids

    def test_has_why_and_refs(self, bad):
        issues = [i for i in bad if i.rule_id == "DS2_button_radius_inconsistency"]
        assert issues[0].why
        assert issues[0].references


# ── DS3 — button padding inconsistency ───────────────────────────────────────

class TestButtonPaddingInconsistency:
    def test_single_button_no_issue(self, thresholds):
        page = {"buttons": [{"padding_top_px": 8.0, "padding_left_px": 16.0,
                              "background_color": "#005fcc", "border_radius_px": 4.0}]}
        issues = analyze(page, thresholds)
        assert not any(i.rule_id == "DS3_button_padding_inconsistency" for i in issues)

    def test_has_why_and_refs(self, bad):
        issues = [i for i in bad if i.rule_id == "DS3_button_padding_inconsistency"]
        if issues:
            assert issues[0].why
            assert issues[0].references


# ── DS4 — no spacing system ───────────────────────────────────────────────────

class TestNoSpacingSystem:
    def test_fires_on_bad_page(self, bad):
        rule_ids = [i.rule_id for i in bad]
        assert "DS4_no_spacing_system" in rule_ids

    def test_not_fire_on_clean_page(self, clean):
        rule_ids = [i.rule_id for i in clean]
        assert "DS4_no_spacing_system" not in rule_ids

    def test_no_spacing_values_no_issue(self, thresholds):
        issues = analyze({"spacing_values_px": []}, thresholds)
        assert not any(i.rule_id == "DS4_no_spacing_system" for i in issues)

    def test_has_why_and_refs(self, bad):
        issues = [i for i in bad if i.rule_id == "DS4_no_spacing_system"]
        assert issues[0].why
        assert issues[0].references


# ── DS5 — colour palette sprawl ───────────────────────────────────────────────

class TestColourPaletteSprawl:
    def test_fires_on_many_colours(self, thresholds):
        # 10 items: #000000 filtered out → 9 distinct colours > threshold of 8
        page = {
            "buttons": [{"background_color": f"#{i:06x}"} for i in range(10)],
            "text_color_pairs": [],
        }
        issues = analyze(page, thresholds)
        assert any(i.rule_id == "DS5_colour_palette_sprawl" for i in issues)

    def test_not_fire_on_few_colours(self, clean):
        rule_ids = [i.rule_id for i in clean]
        assert "DS5_colour_palette_sprawl" not in rule_ids


# ── DS6 — card padding inconsistency ─────────────────────────────────────────

class TestCardPaddingInconsistency:
    def test_fires_when_cards_differ_by_more_than_8px(self, thresholds):
        page = {
            "cards": [
                {"padding_top_px": 24.0, "padding_right_px": 24.0,
                 "padding_bottom_px": 24.0, "padding_left_px": 24.0},
                {"padding_top_px": 4.0, "padding_right_px": 4.0,
                 "padding_bottom_px": 4.0, "padding_left_px": 4.0},
            ]
        }
        issues = analyze(page, thresholds)
        assert any(i.rule_id == "DS6_card_padding_inconsistency" for i in issues)

    def test_not_fire_on_single_card(self, thresholds):
        page = {"cards": [{"padding_top_px": 12.0, "padding_right_px": 12.0,
                            "padding_bottom_px": 12.0, "padding_left_px": 12.0}]}
        issues = analyze(page, thresholds)
        assert not any(i.rule_id == "DS6_card_padding_inconsistency" for i in issues)


# ── integration — all issues have why + references ───────────────────────────

class TestAllIssuesHaveLearning:
    def test_all_bad_page_issues_have_why(self, bad):
        for i in bad:
            assert i.why, f"{i.rule_id} missing why"

    def test_all_bad_page_issues_have_refs(self, bad):
        for i in bad:
            assert i.references, f"{i.rule_id} missing references"
