from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def _distinct_backgrounds(buttons: list[dict]) -> list[str]:
    seen: list[str] = []
    for btn in buttons:
        color = btn.get("background_color", "").lower()
        if color and color not in seen:
            seen.append(color)
    return seen


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["buttons"]
    buttons = parsed_page.get("buttons", [])

    if not buttons:
        return issues

    # B1 — too many distinct button styles (background colour as proxy for style)
    distinct_bg = _distinct_backgrounds(buttons)
    if len(distinct_bg) > t["max_distinct_styles"]:
        issues.append(Issue(
            rule_id="B1_button_style_count",
            category=Category.CONSISTENCY,
            severity=Severity.HIGH,
            confidence=0.85,
            message=(
                f"{len(distinct_bg)} distinct button background colours detected "
                f"(max recommended: {t['max_distinct_styles']})."
            ),
            recommendation=(
                "Consolidate to one primary button style and at most one secondary/ghost style. "
                "Define them as design tokens."
            ),
            evidence=f"Background colours: {', '.join(distinct_bg)}",
            estimated_time="30 minutes",
        ))

    # B2 — inconsistent border-radius
    radii = [btn.get("border_radius_px", 0) for btn in buttons]
    if radii and (max(radii) - min(radii)) > t["max_border_radius_variance_px"]:
        issues.append(Issue(
            rule_id="B2_border_radius_variance",
            category=Category.CONSISTENCY,
            severity=Severity.MEDIUM,
            confidence=0.9,
            message=(
                f"Button border-radius ranges from {min(radii)}px to {max(radii)}px — "
                "inconsistent across the UI."
            ),
            recommendation="Pick one border-radius value for all buttons and apply it via a design token.",
            evidence=f"Radii found: {sorted(set(radii))}",
            estimated_time="10 minutes",
        ))

    # B3 — missing focus styles (accessibility)
    no_focus = [btn for btn in buttons if not btn.get("has_focus_style", True)]
    if no_focus:
        issues.append(Issue(
            rule_id="B3_focus_style",
            category=Category.ACCESSIBILITY,
            severity=Severity.HIGH,
            confidence=0.95,
            message=f"{len(no_focus)} button(s) have no visible focus style.",
            recommendation=(
                "Add a visible :focus-visible outline to all interactive elements. "
                "E.g. outline: 2px solid #005fcc; outline-offset: 2px;"
            ),
            evidence=f"Buttons without focus style: {[b['text'] for b in no_focus]}",
            estimated_time="15 minutes",
        ))

    # B4 — touch target too small
    small_targets = [
        btn for btn in buttons
        if btn.get("height_px", 44) < t["min_touch_target_px"]
    ]
    if small_targets:
        issues.append(Issue(
            rule_id="B4_touch_target",
            category=Category.ACCESSIBILITY,
            severity=Severity.MEDIUM,
            confidence=0.8,
            message=(
                f"{len(small_targets)} button(s) have a height below the "
                f"{t['min_touch_target_px']}px minimum touch target."
            ),
            recommendation=f"Ensure all buttons are at least {t['min_touch_target_px']}px tall (WCAG 2.5.5).",
            evidence=f"Heights: {[b['height_px'] for b in small_targets]}",
            estimated_time="10 minutes",
        ))

    return issues
