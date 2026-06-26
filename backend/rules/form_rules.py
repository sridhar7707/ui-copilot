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
            ))

    return issues
