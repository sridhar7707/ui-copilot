"""
Module 9 — Claude Prompt Generator.
"""
from __future__ import annotations

import pytest

from backend.services import prompt_generator, scoring_engine
from tests.fixtures import bad_page, clean_page


@pytest.fixture
def bad_prompt():
    return prompt_generator.generate(scoring_engine.analyze(bad_page()))


@pytest.fixture
def clean_prompt():
    return prompt_generator.generate(scoring_engine.analyze(clean_page()))


class TestPromptStructure:
    def test_returns_string(self, bad_prompt):
        assert isinstance(bad_prompt, str)

    def test_not_empty(self, bad_prompt):
        assert len(bad_prompt) > 100

    def test_has_title_heading(self, bad_prompt):
        assert "# UI/UX Improvement Task" in bad_prompt

    def test_has_category_scores_section(self, bad_prompt):
        assert "## Category Scores" in bad_prompt

    def test_includes_overall_score(self, bad_prompt):
        assert "/100" in bad_prompt

    def test_has_high_impact_section(self, bad_prompt):
        assert "## High-Impact Fixes" in bad_prompt

    def test_has_quick_wins_section(self, bad_prompt):
        assert "## Quick Wins" in bad_prompt

    def test_has_accessibility_section(self, bad_prompt):
        assert "## Accessibility Fixes" in bad_prompt

    def test_has_footer(self, bad_prompt):
        assert "UICopilot" in bad_prompt

    def test_rule_ids_appear(self, bad_prompt):
        # at least some rule IDs should be present
        assert any(r in bad_prompt for r in ["S1_", "T1_", "B3_", "F1_", "C1_"])


class TestPromptContent:
    def test_recommendations_are_included(self, bad_prompt):
        # recommendation text from at least one high-impact issue
        result = scoring_engine.analyze(bad_page())
        if result.high_impact:
            assert result.high_impact[0].rule_id in bad_prompt

    def test_why_appears_for_high_impact(self, bad_prompt):
        assert "Why it matters:" in bad_prompt

    def test_references_appear_for_high_impact(self, bad_prompt):
        assert "Reference products:" in bad_prompt

    def test_clean_page_still_produces_prompt(self, clean_prompt):
        assert isinstance(clean_prompt, str)
        assert "# UI/UX Improvement Task" in clean_prompt
        assert "/100" in clean_prompt


class TestPromptIsIdempotent:
    def test_same_input_same_output(self):
        result = scoring_engine.analyze(bad_page())
        p1 = prompt_generator.generate(result)
        p2 = prompt_generator.generate(result)
        assert p1 == p2
