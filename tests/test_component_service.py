"""
Module 20 — Component Library tests.

All tests are deterministic: no DB, no network, pure dict input.
"""
from __future__ import annotations

from backend.services import component_service


# ── helpers ───────────────────────────────────────────────────────────────────

def _analysis(components: dict | None = None, score: float = 80.0) -> dict:
    data: dict = {"overall_score": score, "issues": []}
    if components is not None:
        data["components"] = components
    return data


def _components(
    buttons: list | None = None,
    cards: list | None = None,
    inputs: list | None = None,
    fonts: list | None = None,
    spacing: list | None = None,
    color_pairs: list | None = None,
    body_font_size: float | None = None,
) -> dict:
    return {
        "buttons": buttons or [],
        "cards": cards or [],
        "inputs": inputs or [],
        "fonts": fonts or [],
        "text_color_pairs": color_pairs or [],
        "spacing_values_px": spacing or [],
        "body_font_size_px": body_font_size,
    }


def _btn(bg: str = "#6366f1", radius: float = 6.0, size: float = 14.0) -> dict:
    return {"background_color": bg, "border_radius_px": radius, "font_size_px": size}


def _card(padding: float = 20.0, radius: float = 8.0) -> dict:
    return {"padding_px": padding, "border_radius_px": radius}


# ── empty / no-data inputs ────────────────────────────────────────────────────

class TestEmpty:
    def test_empty_analyses(self):
        out = component_service.build([])
        assert out["coverage"]["total_pages"] == 0
        assert out["coverage"]["pages_with_components"] == 0
        assert out["buttons"]["total_detected"] == 0

    def test_analyses_without_component_snapshots(self):
        out = component_service.build([_analysis(), _analysis()])
        assert out["coverage"]["total_pages"] == 2
        assert out["coverage"]["pages_with_components"] == 0
        assert out["buttons"]["total_detected"] == 0

    def test_on_8pt_grid_none_when_no_spacing(self):
        out = component_service.build([_analysis(_components())])
        assert out["spacing"]["on_8pt_grid"] is None


# ── coverage ──────────────────────────────────────────────────────────────────

class TestCoverage:
    def test_counts_pages_with_and_without_data(self):
        analyses = [
            _analysis(_components()),
            _analysis(),          # no component snapshot
            _analysis(_components()),
        ]
        out = component_service.build(analyses)
        assert out["coverage"]["total_pages"] == 3
        assert out["coverage"]["pages_with_components"] == 2


# ── buttons ───────────────────────────────────────────────────────────────────

class TestButtons:
    def test_counts_buttons_across_pages(self):
        a1 = _analysis(_components(buttons=[_btn(), _btn()]))
        a2 = _analysis(_components(buttons=[_btn(bg="#fff")]))
        out = component_service.build([a1, a2])
        assert out["buttons"]["total_detected"] == 3

    def test_deduplicates_background_colors(self):
        color = "#6366f1"
        a = _analysis(_components(buttons=[_btn(bg=color), _btn(bg=color)]))
        out = component_service.build([a])
        assert out["buttons"]["background_colors"].count(color) == 1

    def test_normalizes_colors_lowercase(self):
        a = _analysis(_components(buttons=[_btn(bg="#FFFFFF"), _btn(bg="#ffffff")]))
        out = component_service.build([a])
        assert len(out["buttons"]["background_colors"]) == 1
        assert "#ffffff" in out["buttons"]["background_colors"]

    def test_style_count_matches_unique_colors(self):
        a = _analysis(_components(buttons=[_btn(bg="#aaa"), _btn(bg="#bbb"), _btn(bg="#aaa")]))
        out = component_service.build([a])
        assert out["buttons"]["style_count"] == 2

    def test_border_radii_sorted(self):
        a = _analysis(_components(buttons=[_btn(radius=8.0), _btn(radius=4.0), _btn(radius=6.0)]))
        out = component_service.build([a])
        assert out["buttons"]["border_radii_px"] == sorted(out["buttons"]["border_radii_px"])

    def test_no_buttons_returns_empty_lists(self):
        a = _analysis(_components(buttons=[]))
        out = component_service.build([a])
        assert out["buttons"]["background_colors"] == []
        assert out["buttons"]["border_radii_px"] == []


# ── cards ─────────────────────────────────────────────────────────────────────

class TestCards:
    def test_counts_cards_across_pages(self):
        a1 = _analysis(_components(cards=[_card(), _card()]))
        a2 = _analysis(_components(cards=[_card(padding=16.0)]))
        out = component_service.build([a1, a2])
        assert out["cards"]["total_detected"] == 3

    def test_deduplicates_padding_values(self):
        a = _analysis(_components(cards=[_card(padding=20.0), _card(padding=20.0)]))
        out = component_service.build([a])
        assert out["cards"]["padding_values_px"].count(20.0) == 1

    def test_padding_sorted(self):
        a = _analysis(_components(cards=[_card(padding=24.0), _card(padding=12.0)]))
        out = component_service.build([a])
        assert out["cards"]["padding_values_px"] == [12.0, 24.0]


# ── typography ────────────────────────────────────────────────────────────────

class TestTypography:
    def test_collects_font_families_from_strings(self):
        a = _analysis(_components(fonts=["Inter", "Roboto"]))
        out = component_service.build([a])
        assert "Inter" in out["typography"]["fonts"]
        assert "Roboto" in out["typography"]["fonts"]

    def test_collects_font_families_from_dicts(self):
        a = _analysis(_components(fonts=[{"family": "Inter", "size_px": 16}]))
        out = component_service.build([a])
        assert "Inter" in out["typography"]["fonts"]

    def test_deduplicates_fonts_across_pages(self):
        a1 = _analysis(_components(fonts=["Inter"]))
        a2 = _analysis(_components(fonts=["Inter", "Roboto"]))
        out = component_service.build([a1, a2])
        assert out["typography"]["fonts"].count("Inter") == 1

    def test_body_font_sizes_collected(self):
        a1 = _analysis(_components(body_font_size=16.0))
        a2 = _analysis(_components(body_font_size=14.0))
        out = component_service.build([a1, a2])
        assert 16.0 in out["typography"]["body_font_sizes_px"]
        assert 14.0 in out["typography"]["body_font_sizes_px"]

    def test_body_font_size_none_skipped(self):
        a = _analysis(_components(body_font_size=None))
        out = component_service.build([a])
        assert out["typography"]["body_font_sizes_px"] == []


# ── spacing ───────────────────────────────────────────────────────────────────

class TestSpacing:
    def test_on_8pt_grid_true(self):
        a = _analysis(_components(spacing=[8.0, 16.0, 24.0, 32.0]))
        out = component_service.build([a])
        assert out["spacing"]["on_8pt_grid"] is True

    def test_on_8pt_grid_false(self):
        a = _analysis(_components(spacing=[8.0, 13.0, 24.0]))
        out = component_service.build([a])
        assert out["spacing"]["on_8pt_grid"] is False

    def test_spacing_values_sorted_and_deduped(self):
        a1 = _analysis(_components(spacing=[16.0, 8.0]))
        a2 = _analysis(_components(spacing=[8.0, 24.0]))
        out = component_service.build([a1, a2])
        vals = out["spacing"]["values_px"]
        assert vals == sorted(set(vals))
        assert vals.count(8.0) == 1

    def test_zero_spacing_excluded_from_grid_check(self):
        a = _analysis(_components(spacing=[0.0, 8.0, 16.0]))
        out = component_service.build([a])
        assert out["spacing"]["on_8pt_grid"] is True


# ── colors ────────────────────────────────────────────────────────────────────

class TestColors:
    def test_color_pairs_deduplicated(self):
        pair = {"text_color": "#fff", "background_color": "#000"}
        a1 = _analysis(_components(color_pairs=[pair]))
        a2 = _analysis(_components(color_pairs=[pair]))
        out = component_service.build([a1, a2])
        assert len(out["colors"]["text_background_pairs"]) == 1

    def test_distinct_color_pairs_all_present(self):
        pairs = [
            {"text_color": "#fff", "background_color": "#000"},
            {"text_color": "#000", "background_color": "#fff"},
        ]
        a = _analysis(_components(color_pairs=pairs))
        out = component_service.build([a])
        assert len(out["colors"]["text_background_pairs"]) == 2
