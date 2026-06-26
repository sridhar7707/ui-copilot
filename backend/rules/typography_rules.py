from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["typography"]

    # T1 — body font size too small
    body_size = parsed_page.get("body_font_size_px")
    if body_size is not None and body_size < t["min_body_size_px"]:
        issues.append(Issue(
            rule_id="T1_body_font_size",
            category=Category.TYPOGRAPHY,
            severity=Severity.HIGH,
            confidence=1.0,
            message=f"Body font size ({body_size}px) is below the recommended minimum ({t['min_body_size_px']}px).",
            recommendation=f"Set body font-size to at least {t['recommended_body_size_px']}px for comfortable reading.",
            evidence=f"font-size: {body_size}px",
            estimated_time="2 minutes",
        ))

    # T2 — too many font families
    fonts = parsed_page.get("fonts", [])
    if len(fonts) > t["max_font_families"]:
        issues.append(Issue(
            rule_id="T2_font_family_count",
            category=Category.TYPOGRAPHY,
            severity=Severity.MEDIUM,
            confidence=0.9,
            message=f"{len(fonts)} font families in use (max recommended: {t['max_font_families']}).",
            recommendation="Limit to two font families: one for headings, one for body text.",
            evidence=f"Fonts found: {', '.join(fonts)}",
            estimated_time="15 minutes",
        ))

    # T3 — line height too tight
    line_height = parsed_page.get("line_height")
    if line_height is not None and line_height < t["line_height_min"]:
        issues.append(Issue(
            rule_id="T3_line_height",
            category=Category.TYPOGRAPHY,
            severity=Severity.MEDIUM,
            confidence=1.0,
            message=f"Line height ({line_height}) is below the comfortable minimum ({t['line_height_min']}).",
            recommendation=f"Set line-height to {t['line_height_min']}–{t['line_height_max']} for readability.",
            evidence=f"line-height: {line_height}",
            estimated_time="2 minutes",
        ))

    # T4 — no clear heading hierarchy (h1 and h2 too similar in size)
    headings = parsed_page.get("headings", [])
    h1_list = [h for h in headings if h["level"] == 1]
    h2_list = [h for h in headings if h["level"] == 2]
    if h1_list and h2_list:
        h1_size = h1_list[0]["font_size_px"]
        h2_size = h2_list[0]["font_size_px"]
        if h2_size > 0 and (h1_size / h2_size) < t["min_h1_h2_ratio"]:
            issues.append(Issue(
                rule_id="T4_heading_hierarchy",
                category=Category.VISUAL_HIERARCHY,
                severity=Severity.HIGH,
                confidence=0.95,
                message=(
                    f"H1 ({h1_size}px) and H2 ({h2_size}px) are too close in size — "
                    f"hierarchy ratio {h1_size / h2_size:.2f} < {t['min_h1_h2_ratio']}."
                ),
                recommendation="Increase the size difference between heading levels to create clear visual hierarchy.",
                evidence=f"h1: {h1_size}px, h2: {h2_size}px",
                estimated_time="5 minutes",
            ))

    # T5 — heading font size too small
    for h in headings:
        if h["level"] <= 2 and h["font_size_px"] < t["min_heading_size_px"]:
            issues.append(Issue(
                rule_id="T5_heading_size",
                category=Category.VISUAL_HIERARCHY,
                severity=Severity.MEDIUM,
                confidence=0.9,
                message=(
                    f"H{h['level']} \"{h['text'][:40]}\" is only {h['font_size_px']}px — "
                    f"too small to establish hierarchy."
                ),
                recommendation=f"H1/H2 should be at least {t['min_heading_size_px']}px.",
                evidence=f"h{h['level']}: font-size {h['font_size_px']}px",
                estimated_time="5 minutes",
            ))

    return issues
