from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["forms"]
    inputs = parsed_page.get("inputs", [])

    for i, inp in enumerate(inputs):
        input_type = inp.get("input_type", "text")
        label = f"Input #{i + 1} ({input_type})"

        # F1 — missing label
        if not inp.get("has_label", True):
            issues.append(Issue(
                rule_id="F1_missing_label",
                category=Category.ACCESSIBILITY,
                severity=Severity.CRITICAL,
                confidence=1.0,
                message=f"{label} has no associated <label> element.",
                recommendation=(
                    "Add a <label for='...'>  element linked via the input's id, "
                    "or use aria-label / aria-labelledby as a fallback."
                ),
                evidence="No <label> or aria-label found for this input.",
                estimated_time="5 minutes",
                why=(
                    "Unlabelled form fields are completely inaccessible to screen readers — "
                    "the screen reader announces only the input type with no context. "
                    "WCAG 1.3.1 and 3.3.2 both require programmatic labels. "
                    "This is the #1 WCAG failure found in government and enterprise audits."
                ),
                references=["WCAG 2.1 SC 1.3.1", "WCAG 2.1 SC 3.3.2", "GOV.UK"],
            ))

        # F2 — placeholder used as label substitute
        if (
            not inp.get("has_label", True)
            and inp.get("placeholder")
            and not inp.get("label_text")
        ):
            issues.append(Issue(
                rule_id="F2_placeholder_as_label",
                category=Category.ACCESSIBILITY,
                severity=Severity.HIGH,
                confidence=0.9,
                message=(
                    f"{label} uses placeholder text as its only label — "
                    "placeholder disappears on focus, leaving users confused."
                ),
                recommendation=(
                    "Replace placeholder-as-label with a persistent <label>. "
                    "Placeholders should show example input, not field names."
                ),
                evidence=f"placeholder: \"{inp.get('placeholder', '')}\"",
                estimated_time="5 minutes",
                why=(
                    "Placeholders disappear the moment a user starts typing, leaving those "
                    "who pause mid-form with no reminder of what the field expects. "
                    "Low-vision users also struggle with placeholder text, which rarely "
                    "meets WCAG contrast requirements. This pattern is explicitly flagged "
                    "as an anti-pattern in WCAG 3.3.2 failure techniques."
                ),
                references=["Nielsen Norman Group", "WCAG 2.1 SC 3.3.2", "GOV.UK"],
            ))

        # F3 — insufficient input padding
        pad = inp.get("padding_px", 0)
        if pad < t["min_input_padding_px"]:
            issues.append(Issue(
                rule_id="F3_input_padding",
                category=Category.COMPONENT_QUALITY,
                severity=Severity.LOW,
                confidence=0.85,
                message=f"{label} padding ({pad}px) is too small — inputs feel cramped.",
                recommendation=f"Set input padding to at least {t['min_input_padding_px']}px (e.g. padding: 8px 12px;).",
                evidence=f"padding: {pad}px",
                estimated_time="5 minutes",
                why=(
                    "Small input padding creates cramped form fields that are hard to tap "
                    "on mobile and visually signal low production quality. "
                    "Inputs with generous padding also have larger click areas, reducing "
                    "mis-clicks. It's the single cheapest change that makes a form feel "
                    "professionally designed."
                ),
                references=["Material Design", "Stripe", "iOS HIG"],
            ))

    return issues
