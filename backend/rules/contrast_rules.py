from __future__ import annotations

from backend.models.issue import Category, Issue, Severity
from backend.utils.color_utils import contrast_ratio


def _is_large_text(font_size_px: float, is_bold: bool, t: dict) -> bool:
    bold_threshold = t.get("large_text_bold_size_px", 14)
    normal_threshold = t.get("large_text_size_px", 18)
    return font_size_px >= normal_threshold or (is_bold and font_size_px >= bold_threshold)


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["contrast"]

    for pair in parsed_page.get("text_color_pairs", []):
        fg = pair["foreground"]
        bg = pair["background"]
        size = pair["font_size_px"]
        bold = pair["is_bold"]
        context = pair["context"]

        try:
            ratio = contrast_ratio(fg, bg)
        except ValueError:
            continue  # skip unparseable colours

        large = _is_large_text(size, bold, t)
        required = t["wcag_aa_large"] if large else t["wcag_aa_normal"]
        label = "large" if large else "normal"

        if ratio < required:
            severity = Severity.HIGH if ratio < 3.0 else Severity.MEDIUM
            issues.append(Issue(
                rule_id="C1_wcag_aa_contrast",
                category=Category.CONTRAST,
                severity=severity,
                confidence=1.0,
                message=(
                    f"{context.capitalize()} text contrast {ratio:.2f}:1 fails WCAG AA "
                    f"({label} text requires {required}:1)."
                ),
                recommendation=(
                    f"Increase contrast between {fg} and {bg} to at least {required}:1. "
                    "Use a contrast checker to find a compliant colour pair."
                ),
                evidence=f"{fg} on {bg} at {size}px {'bold' if bold else ''}".strip(),
                estimated_time="10 minutes",
            ))
            # Also flag as accessibility issue
            issues.append(Issue(
                rule_id="C1_wcag_aa_contrast_a11y",
                category=Category.ACCESSIBILITY,
                severity=severity,
                confidence=1.0,
                message=(
                    f"Low contrast ({ratio:.2f}:1) on {context} text — "
                    "users with low vision will struggle to read this."
                ),
                recommendation=f"Target a contrast ratio of at least {required}:1 (WCAG AA).",
                evidence=f"{fg} on {bg}",
                estimated_time="10 minutes",
            ))

    return issues
