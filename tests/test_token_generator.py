"""
Module 12 — Design Token Generator tests.

All tests are deterministic: no API calls, no disk access beyond
loading the scoring config (which is a fixture of the project).
"""
from __future__ import annotations


from backend.models.analysis import AnalysisResult
from backend.models.issue import Category, Issue, Severity
from backend.services import token_generator


# ── helpers ───────────────────────────────────────────────────────────────────

def _result(issues: list[Issue] | None = None) -> AnalysisResult:
    return AnalysisResult(overall_score=75.0, category_scores=[], issues=issues or [])


def _issue(rule_id: str) -> Issue:
    return Issue(
        rule_id=rule_id,
        category=Category.ACCESSIBILITY,
        severity=Severity.HIGH,
        confidence=0.9,
        message="test",
        recommendation="fix",
        evidence="n/a",
        estimated_time="5 minutes",
        estimated_gain=2.0,
    )


# ── basic output ──────────────────────────────────────────────────────────────

class TestBasicOutput:
    def test_returns_string(self):
        assert isinstance(token_generator.generate(_result()), str)

    def test_non_empty(self):
        assert len(token_generator.generate(_result())) > 100

    def test_score_in_header(self):
        assert "75.0/100" in token_generator.generate(_result())

    def test_is_css_not_json(self):
        out = token_generator.generate(_result())
        assert ":root {" in out
        assert "--" in out


# ── color tokens ──────────────────────────────────────────────────────────────

class TestColorTokens:
    def test_primary_color_token_present(self):
        assert "--color-primary:" in token_generator.generate(_result())

    def test_surface_token_present(self):
        assert "--color-surface:" in token_generator.generate(_result())

    def test_text_tokens_present(self):
        out = token_generator.generate(_result())
        assert "--color-text-primary:" in out
        assert "--color-text-secondary:" in out
        assert "--color-text-muted:" in out

    def test_semantic_alias_present(self):
        out = token_generator.generate(_result())
        assert "--color-border:" in out
        assert "--color-success:" in out
        assert "--color-danger:" in out

    def test_contrast_issue_uses_accessible_primary(self):
        result = _result([_issue("C1_wcag_aa_contrast")])
        out = token_generator.generate(result)
        assert "#005fcc" in out

    def test_no_contrast_issue_uses_default_primary(self):
        out = token_generator.generate(_result())
        assert "#0066ff" in out


# ── spacing tokens ────────────────────────────────────────────────────────────

class TestSpacingTokens:
    def test_space_4_present(self):
        assert "--space-4:" in token_generator.generate(_result())

    def test_space_8_present(self):
        assert "--space-8:" in token_generator.generate(_result())

    def test_space_16_present(self):
        assert "--space-16:" in token_generator.generate(_result())

    def test_space_32_present(self):
        assert "--space-32:" in token_generator.generate(_result())

    def test_semantic_space_alias_present(self):
        out = token_generator.generate(_result())
        assert "--space-page-x:" in out
        assert "--space-component:" in out


# ── radius tokens ─────────────────────────────────────────────────────────────

class TestRadiusTokens:
    def test_radius_md_present(self):
        assert "--radius-md:" in token_generator.generate(_result())

    def test_radius_full_present(self):
        assert "--radius-full:" in token_generator.generate(_result())

    def test_semantic_radius_aliases(self):
        out = token_generator.generate(_result())
        assert "--radius-button:" in out
        assert "--radius-card:" in out


# ── elevation / shadow tokens ─────────────────────────────────────────────────

class TestElevationTokens:
    def test_shadow_sm_present(self):
        assert "--shadow-sm:" in token_generator.generate(_result())

    def test_shadow_xl_present(self):
        assert "--shadow-xl:" in token_generator.generate(_result())

    def test_semantic_shadow_aliases(self):
        out = token_generator.generate(_result())
        assert "--shadow-card:" in out
        assert "--shadow-dialog:" in out
        assert "--shadow-focus:" in out


# ── typography tokens ─────────────────────────────────────────────────────────

class TestTypographyTokens:
    def test_font_family_tokens(self):
        out = token_generator.generate(_result())
        assert "--font-sans:" in out
        assert "--font-mono:" in out

    def test_size_scale_present(self):
        out = token_generator.generate(_result())
        assert "--text-xs:" in out
        assert "--text-base:" in out
        assert "--text-4xl:" in out

    def test_weight_tokens(self):
        out = token_generator.generate(_result())
        assert "--font-weight-normal:" in out
        assert "--font-weight-bold:" in out

    def test_line_height_tokens(self):
        out = token_generator.generate(_result())
        assert "--leading-normal:" in out
        assert "--leading-tight:" in out

    def test_letter_spacing_tokens(self):
        out = token_generator.generate(_result())
        assert "--tracking-tight:" in out
        assert "--tracking-wide:" in out

    def test_semantic_font_aliases(self):
        out = token_generator.generate(_result())
        assert "--font-size-body:" in out
        assert "--line-height-body:" in out


# ── animation tokens ──────────────────────────────────────────────────────────

class TestAnimationTokens:
    def test_duration_tokens(self):
        out = token_generator.generate(_result())
        assert "--duration-fast:" in out
        assert "--duration-normal:" in out
        assert "--duration-slow:" in out

    def test_easing_tokens(self):
        out = token_generator.generate(_result())
        assert "--ease-default:" in out
        assert "--ease-spring:" in out

    def test_transition_shorthands(self):
        out = token_generator.generate(_result())
        assert "--transition-colors:" in out
        assert "--transition-opacity:" in out


# ── dark mode ─────────────────────────────────────────────────────────────────

class TestDarkMode:
    def test_dark_mode_media_query_present(self):
        assert "prefers-color-scheme: dark" in token_generator.generate(_result())

    def test_dark_surface_token_present(self):
        assert "#0f172a" in token_generator.generate(_result())


# ── idempotency ───────────────────────────────────────────────────────────────

class TestIdempotency:
    def test_same_result_same_output(self):
        r = _result()
        assert token_generator.generate(r) == token_generator.generate(r)
