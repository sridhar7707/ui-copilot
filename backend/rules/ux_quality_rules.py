"""
UX Quality rules — detect gaps in customer-friendliness that visual scores miss:
missing error states, absent empty-state guidance, vague form submit text,
no skip navigation for keyboard users.
"""
from __future__ import annotations

from backend.models.issue import Category, Issue, Severity

_CAT = Category.UX_QUALITY

_GENERIC_SUBMIT_TEXT = frozenset({
    "submit", "send", "ok", "yes", "confirm", "done", "next", "continue",
    "proceed", "go", "click here", "press here",
})


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []

    _check_error_states(parsed_page, issues)
    _check_empty_states(parsed_page, issues)
    _check_form_submit_text(parsed_page, issues)
    _check_skip_link(parsed_page, issues)

    return issues


# ── UX1 — missing error states ────────────────────────────────────────────────

def _check_error_states(parsed_page: dict, issues: list[Issue]) -> None:
    inputs = parsed_page.get("inputs", [])
    has_error = parsed_page.get("has_error_states", False)

    if inputs and not has_error:
        issues.append(Issue(
            rule_id="UX1_missing_error_states",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.70,
            message=(
                f"Form with {len(inputs)} input(s) detected but no error state "
                "styling found (aria-invalid, .error, .is-invalid classes)."
            ),
            recommendation=(
                "Add visible error states to every form field: "
                "red border, inline error message below the field, aria-invalid='true', "
                "and aria-describedby pointing to the error element. "
                "Error messages must explain what went wrong AND how to fix it."
            ),
            evidence=f"inputs={len(inputs)}, has_error_states=False",
            estimated_time="2 hours",
            why=(
                "When users make a mistake in a form, their #1 need is clear, contextual "
                "feedback. Forms without error states force users to guess what went wrong. "
                "The Baymard Institute found that poor inline validation is the #2 reason "
                "for form abandonment. WCAG 3.3.1 (Level A) requires error identification."
            ),
            references=["WCAG 3.3.1", "Baymard Form Usability", "Nielsen Form Design"],
        ))


# ── UX2 — missing empty states ────────────────────────────────────────────────

def _check_empty_states(parsed_page: dict, issues: list[Issue]) -> None:
    has_empty = parsed_page.get("has_empty_states", False)
    inputs = parsed_page.get("inputs", [])
    tables = parsed_page.get("tables", [])

    # Only flag if there are data-bearing components (tables/inputs imply dynamic content)
    if not has_empty and (tables or inputs):
        issues.append(Issue(
            rule_id="UX2_missing_empty_states",
            category=_CAT,
            severity=Severity.LOW,
            confidence=0.60,
            message=(
                "No empty state UI detected — data components (tables/forms) exist but "
                "there are no '.empty', '.no-results', or '.placeholder' patterns."
            ),
            recommendation=(
                "Add empty states for every data component: "
                "a short explanation ('No items yet'), an illustrative icon, "
                "and a next-step CTA ('Create your first item →'). "
                "Empty states convert confused users into active ones."
            ),
            evidence=f"has_empty_states=False, tables={len(tables)}, inputs={len(inputs)}",
            estimated_time="3 hours",
            why=(
                "Empty states are the most overlooked UX moment. A blank table or empty "
                "list with no guidance leaves users wondering if the product is broken. "
                "Products with well-designed empty states (Slack, Notion, Linear) use them "
                "as onboarding opportunities — showing users exactly what to do next."
            ),
            references=["Luke Wroblewski — Empty States", "Nielsen Norman Group", "Material Design"],
        ))


# ── UX3 — generic form submit button text ─────────────────────────────────────

def _check_form_submit_text(parsed_page: dict, issues: list[Issue]) -> None:
    buttons = parsed_page.get("buttons", [])
    inputs = parsed_page.get("inputs", [])

    if not inputs:
        return  # No forms, skip

    submit_buttons = [
        b for b in buttons
        if b.get("text", "").lower().strip() in _GENERIC_SUBMIT_TEXT
    ]

    if submit_buttons:
        weak_texts = list({b["text"] for b in submit_buttons})[:3]
        issues.append(Issue(
            rule_id="UX3_generic_submit_text",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.80,
            message=(
                f"{len(submit_buttons)} form submit button(s) use generic text: "
                f"{', '.join(repr(t) for t in weak_texts)}."
            ),
            recommendation=(
                "Replace with outcome-specific text that confirms what happens next: "
                "'Create Account', 'Send Message', 'Save Changes', 'Subscribe Now'. "
                "The button text is the last micro-decision before submission."
            ),
            evidence=f"generic_submit_buttons={weak_texts}",
            estimated_time="10 minutes",
            why=(
                "Generic submit text ('Submit', 'Send') creates a moment of hesitation "
                "— the user must think 'submit what? to where?'. Descriptive button labels "
                "reduce cognitive load, set expectations, and give users confidence. "
                "Paul Boag's research shows outcome-specific labels improve form completion "
                "by 15–30% over generic alternatives."
            ),
            references=["Paul Boag — Form Design", "Copyhackers", "UX Myths"],
        ))


# ── UX4 — missing skip navigation ────────────────────────────────────────────

def _check_skip_link(parsed_page: dict, issues: list[Issue]) -> None:
    has_skip = parsed_page.get("has_skip_link", False)
    inputs = parsed_page.get("inputs", [])
    buttons = parsed_page.get("buttons", [])

    # Only flag on pages with interactive elements (forms/buttons suggest real apps)
    if not has_skip and (len(inputs) + len(buttons) >= 3):
        issues.append(Issue(
            rule_id="UX4_missing_skip_link",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.85,
            message="No 'Skip to main content' link detected on a page with interactive elements.",
            recommendation=(
                "Add a visually-hidden skip link as the very first element in <body>: "
                "<a href='#main-content' class='skip-link'>Skip to main content</a>. "
                "Make it visible on focus. Link target must be the id of the main region."
            ),
            evidence=f"has_skip_link=False, interactive_elements={len(inputs)+len(buttons)}",
            estimated_time="20 minutes",
            why=(
                "Keyboard and screen reader users tab through every navigation link before "
                "reaching the main content — on a page with 20 nav links, that's 20 Tab presses. "
                "A skip link lets them jump directly to content. WCAG 2.4.1 (Level A) requires "
                "a mechanism to bypass repeating navigation blocks."
            ),
            references=["WCAG 2.4.1", "WebAIM Skip Navigation", "A11y Project"],
        ))
