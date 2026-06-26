from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def _on_grid(value: float, base: float, tolerance: float = 0.5) -> bool:
    if value == 0:
        return True
    return (value % base) <= tolerance or (base - value % base) <= tolerance


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["spacing"]

    # S1 — button padding too small
    for btn in parsed_page.get("buttons", []):
        too_short = btn["padding_top_px"] < t["button_min_padding_y_px"]
        too_narrow = btn["padding_left_px"] < t["button_min_padding_x_px"]
        if too_short or too_narrow:
            issues.append(Issue(
                rule_id="S1_button_padding",
                category=Category.SPACING,
                severity=Severity.HIGH,
                confidence=1.0,
                message=(
                    f"Button \"{btn['text']}\" has insufficient padding "
                    f"({btn['padding_top_px']}px × {btn['padding_left_px']}px)."
                ),
                recommendation=(
                    f"Set button padding to at least {t['button_min_padding_y_px']}px vertical "
                    f"and {t['button_min_padding_x_px']}px horizontal."
                ),
                evidence=(
                    f"padding-top:{btn['padding_top_px']}px; "
                    f"padding-left:{btn['padding_left_px']}px"
                ),
                estimated_time="5 minutes",
                why=(
                    "Cramped buttons are harder to click on touch devices and feel cheap. "
                    "WCAG 2.5.8 requires a 24px minimum target area, but leading products "
                    "use 44px+ height to reduce mis-taps and convey quality."
                ),
                references=["Apple HIG", "Material Design", "WCAG 2.5.8"],
            ))

    # S2 — card padding too small
    for i, card in enumerate(parsed_page.get("cards", [])):
        min_pad = min(
            card["padding_top_px"],
            card["padding_right_px"],
            card["padding_bottom_px"],
            card["padding_left_px"],
        )
        if min_pad < t["card_min_padding_px"]:
            issues.append(Issue(
                rule_id="S2_card_padding",
                category=Category.SPACING,
                severity=Severity.MEDIUM,
                confidence=0.9,
                message=(
                    f"Card #{i + 1} padding ({min_pad}px) is below the "
                    f"recommended minimum ({t['card_min_padding_px']}px)."
                ),
                recommendation=f"Set card padding to at least {t['card_min_padding_px']}px on all sides.",
                evidence=(
                    f"padding:{card['padding_top_px']}px {card['padding_right_px']}px "
                    f"{card['padding_bottom_px']}px {card['padding_left_px']}px"
                ),
                estimated_time="5 minutes",
                why=(
                    "Insufficient card padding compresses content against the edge, "
                    "removing the visual breathing room that separates content from chrome. "
                    "White space inside a card communicates the card's boundaries and makes "
                    "the content feel considered, not thrown together."
                ),
                references=["Refactoring UI", "Notion", "Stripe"],
            ))

    # S3 — spacing values off the 8pt grid → consistency issue
    base = t["grid_base_px"]
    tol = t.get("off_grid_tolerance", 0.5)
    off_grid = [
        v for v in parsed_page.get("spacing_values_px", [])
        if v > 0 and not _on_grid(v, base, tol)
    ]
    if len(off_grid) > 2:
        sample = sorted({round(v) for v in off_grid})[:5]
        issues.append(Issue(
            rule_id="S3_off_grid_spacing",
            category=Category.CONSISTENCY,
            severity=Severity.MEDIUM,
            confidence=0.8,
            message=f"{len(off_grid)} spacing values are not on the {base}pt grid.",
            recommendation=(
                f"Adopt a strict {base}pt spacing scale "
                f"(e.g. 8, 16, 24, 32, 48 px) and remove arbitrary values."
            ),
            evidence=f"Off-grid values (sample): {sample}",
            estimated_time="30 minutes",
            why=(
                "Arbitrary spacing values accumulate silently into a visually inconsistent UI. "
                "An 8pt grid means every spacing decision is predictable — developers can "
                "reason about layout without opening a design file, and the result looks "
                "intentional rather than hand-coded."
            ),
            references=["Tailwind CSS", "Material Design", "8pt Grid System"],
        ))

    return issues
