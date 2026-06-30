"""
Interactivity rules — detect static UIs that feel unresponsive: no hover states,
no CSS transitions, focus outline removed without replacement, no keyboard
skip link for long-nav pages.
"""
from __future__ import annotations

from backend.models.issue import Category, Issue, Severity

_CAT = Category.INTERACTIVITY


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []

    _check_hover_states(parsed_page, issues)
    _check_transitions(parsed_page, issues)
    _check_focus_outline_removed(parsed_page, issues)

    return issues


# ── INT1 — missing hover states ───────────────────────────────────────────────

def _check_hover_states(parsed_page: dict, issues: list[Issue]) -> None:
    has_hover = parsed_page.get("has_hover_styles", False)
    buttons = parsed_page.get("buttons", [])
    inputs = parsed_page.get("inputs", [])
    cta_texts = parsed_page.get("cta_texts", [])

    # Only flag pages with interactive elements
    interactive_count = len(buttons) + len(inputs) + len(cta_texts)
    if not has_hover and interactive_count >= 2:
        issues.append(Issue(
            rule_id="INT1_missing_hover_states",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.75,
            message=(
                f"No :hover CSS rules detected on a page with {interactive_count} "
                "interactive elements — buttons/links give no visual feedback on hover."
            ),
            recommendation=(
                "Add :hover styles to all clickable elements: "
                "button:hover { background-color: darken(primary, 10%); transform: translateY(-1px); } "
                "a:hover { text-decoration: underline; color: darken(link, 15%); }. "
                "Hover states should always change at least one visual property."
            ),
            evidence=f"has_hover_styles=False, interactive_elements={interactive_count}",
            estimated_time="45 minutes",
            why=(
                "Hover states are the primary affordance signal for desktop users — "
                "they confirm 'this element is clickable' before the click. "
                "Without hover feedback, users hesitate: 'Is this a button or just text?'. "
                "Desktop users spend ~200ms on hover before clicking — that's 200ms of "
                "expected feedback. Missing it makes the UI feel broken or unfinished."
            ),
            references=["Nielsen Norman Group — Affordances", "WCAG 2.4.13", "Material Design States"],
        ))


# ── INT2 — no CSS transitions ─────────────────────────────────────────────────

def _check_transitions(parsed_page: dict, issues: list[Issue]) -> None:
    has_transitions = parsed_page.get("has_transitions", False)
    buttons = parsed_page.get("buttons", [])
    inputs = parsed_page.get("inputs", [])

    interactive_count = len(buttons) + len(inputs)
    if not has_transitions and interactive_count >= 2:
        issues.append(Issue(
            rule_id="INT2_no_transitions",
            category=_CAT,
            severity=Severity.LOW,
            confidence=0.70,
            message=(
                f"No CSS transitions or animations detected on a page with "
                f"{interactive_count} interactive elements."
            ),
            recommendation=(
                "Add subtle transitions to interactive elements: "
                "button { transition: background-color 150ms ease, transform 100ms ease; } "
                "input:focus { transition: border-color 200ms ease, box-shadow 200ms ease; }. "
                "Keep durations 100–300ms for state changes, 200–500ms for reveals."
            ),
            evidence=f"has_transitions=False, interactive_elements={interactive_count}",
            estimated_time="30 minutes",
            why=(
                "Instant state changes (button click, input focus, modal open) feel "
                "abrupt and cheap. Micro-transitions (100–300ms) communicate state "
                "change while feeling polished and intentional. Google's Material Design "
                "and Apple's HIG both mandate motion as a core design primitive. "
                "Studies show subtle motion increases perceived quality and user trust."
            ),
            references=["Material Design Motion", "Apple HIG Animation", "val Head — CSS Animations"],
        ))


# ── INT3 — focus outline removed ─────────────────────────────────────────────

def _check_focus_outline_removed(parsed_page: dict, issues: list[Issue]) -> None:
    outline_removed = parsed_page.get("has_focus_outline_removed", False)

    if outline_removed:
        issues.append(Issue(
            rule_id="INT3_focus_outline_removed",
            category=Category.ACCESSIBILITY,
            severity=Severity.HIGH,
            confidence=0.90,
            message=(
                "CSS contains `outline: none` or `outline: 0` — "
                "keyboard focus indicator is removed, breaking keyboard navigation."
            ),
            recommendation=(
                "Never remove outline globally. Instead: "
                ":focus { outline: none; } "
                ":focus-visible { outline: 3px solid #005fcc; outline-offset: 2px; } "
                "This hides the ring for mouse users while preserving it for keyboard users."
            ),
            evidence="has_focus_outline_removed=True",
            estimated_time="20 minutes",
            why=(
                "Removing outline: none without a replacement means keyboard users "
                "lose all focus visibility — they cannot tell which element is active. "
                "This is one of the most common accessibility anti-patterns and a direct "
                "WCAG 2.4.7 (Level AA) violation. It makes the UI completely unusable for "
                "keyboard-only users, including many people with motor disabilities."
            ),
            references=["WCAG 2.4.7", "WebAIM Keyboard Accessibility", "CSS Tricks :focus-visible"],
        ))
