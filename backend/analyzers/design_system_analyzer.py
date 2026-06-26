"""
Module 4 — Design System Detection.

Detects inconsistencies in the design system: button style fragmentation,
border-radius variance, spacing grid violations, and colour palette sprawl.
Pure analysis — no API calls, no DB.
"""
from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    """Return design-system consistency issues for the parsed page."""
    t_btn = thresholds["buttons"]
    t_sp = thresholds["spacing"]
    issues: list[Issue] = []

    issues.extend(_check_button_consistency(parsed_page, t_btn))
    issues.extend(_check_spacing_grid(parsed_page, t_sp))
    issues.extend(_check_colour_palette(parsed_page))
    issues.extend(_check_card_consistency(parsed_page))

    return issues


# ── button consistency ────────────────────────────────────────────────────────

def _check_button_consistency(parsed_page: dict, t: dict) -> list[Issue]:
    issues: list[Issue] = []
    buttons = parsed_page.get("buttons", [])
    if len(buttons) < 2:
        return issues

    # DS1 — too many distinct background colours
    bg_colors = list({b.get("background_color", "").lower() for b in buttons if b.get("background_color")})
    if len(bg_colors) > t.get("max_distinct_styles", 2):
        issues.append(Issue(
            rule_id="DS1_button_color_palette",
            category=Category.CONSISTENCY,
            severity=Severity.HIGH,
            confidence=0.9,
            message=(
                f"Design system has {len(bg_colors)} distinct button colours — "
                "no clear primary/secondary hierarchy."
            ),
            recommendation=(
                "Define exactly 2 button variants: primary (solid brand colour) and "
                "secondary (ghost/outline). Store as CSS variables."
            ),
            evidence=f"Colours detected: {', '.join(sorted(bg_colors))}",
            estimated_time="1 hour",
            why=(
                "A fragmented button palette signals the absence of a design system. "
                "When each developer picks a button colour independently, the product "
                "looks assembled, not designed. Two variants cover 95% of real use cases."
            ),
            references=["Stripe", "Linear", "Shopify Polaris"],
        ))

    # DS2 — inconsistent border-radius
    radii = list({b.get("border_radius_px", 0) for b in buttons})
    if len(radii) > 1 and (max(radii) - min(radii)) > t.get("max_border_radius_variance_px", 4):
        issues.append(Issue(
            rule_id="DS2_button_radius_inconsistency",
            category=Category.CONSISTENCY,
            severity=Severity.MEDIUM,
            confidence=0.9,
            message=(
                f"Button border-radius has {len(radii)} distinct values "
                f"({sorted(radii)}) — no single design token in use."
            ),
            recommendation=(
                "Set one border-radius value for all buttons via --btn-radius CSS variable. "
                "Common choices: 4px (square), 6px (soft), 9999px (pill)."
            ),
            evidence=f"Radii found: {sorted(radii)}",
            estimated_time="15 minutes",
            why=(
                "Border-radius is the most visible 'personality' token of a design system. "
                "Inconsistency here signals that components were built independently "
                "rather than from a shared token. It is almost always a 10-minute fix."
            ),
            references=["Tailwind CSS", "Material Design", "Figma Variables"],
        ))

    # DS3 — padding inconsistency across buttons
    pad_combos = list({
        (b.get("padding_top_px", 0), b.get("padding_left_px", 0))
        for b in buttons
    })
    if len(pad_combos) > 2:
        issues.append(Issue(
            rule_id="DS3_button_padding_inconsistency",
            category=Category.CONSISTENCY,
            severity=Severity.LOW,
            confidence=0.8,
            message=(
                f"Buttons use {len(pad_combos)} distinct padding combinations — "
                "no shared sizing scale."
            ),
            recommendation=(
                "Standardise on 2 button sizes: default (8px 16px) and small (4px 12px). "
                "Apply via .btn and .btn-sm classes using CSS variables."
            ),
            evidence=f"Padding combos (top, left): {sorted(pad_combos)}",
            estimated_time="20 minutes",
            why=(
                "Multiple button sizes without a formal small/medium/large naming convention "
                "create maintenance overhead — every new screen needs a judgment call about "
                "which size to use. Two named sizes cover every practical scenario."
            ),
            references=["Material Design", "Bootstrap", "Tailwind CSS"],
        ))

    return issues


# ── spacing grid ──────────────────────────────────────────────────────────────

def _check_spacing_grid(parsed_page: dict, t: dict) -> list[Issue]:
    issues: list[Issue] = []
    base = t.get("grid_base_px", 8)
    tol = t.get("off_grid_tolerance", 0.5)
    spacing = parsed_page.get("spacing_values_px", [])

    if not spacing:
        return issues

    def on_grid(v: float) -> bool:
        if v == 0:
            return True
        return (v % base) <= tol or (base - v % base) <= tol

    off = [v for v in spacing if not on_grid(v)]
    pct = len(off) / len(spacing)

    if pct > 0.5 and len(off) > 3:
        sample = sorted({round(v) for v in off})[:6]
        issues.append(Issue(
            rule_id="DS4_no_spacing_system",
            category=Category.CONSISTENCY,
            severity=Severity.HIGH,
            confidence=0.85,
            message=(
                f"{pct:.0%} of spacing values ({len(off)}/{len(spacing)}) are off the "
                f"{base}pt grid — no spacing system detected."
            ),
            recommendation=(
                f"Adopt a strict {base}pt spacing system. Replace arbitrary values with "
                f"the nearest multiple of {base}: 4, 8, 12, 16, 24, 32, 48 px."
            ),
            evidence=f"Off-grid values (sample): {sample}",
            estimated_time="2 hours",
            why=(
                "A spacing system is the foundation of visual consistency. Without it, "
                "margins and paddings grow organically into arbitrary values. "
                "An 8pt grid means every layout decision is instantly verifiable — "
                "divide by 8 and the number should be a whole integer."
            ),
            references=["8pt Grid System", "Tailwind CSS", "Material Design"],
        ))

    return issues


# ── colour palette ────────────────────────────────────────────────────────────

def _check_colour_palette(parsed_page: dict) -> list[Issue]:
    issues: list[Issue] = []
    buttons = parsed_page.get("buttons", [])
    text_pairs = parsed_page.get("text_color_pairs", [])

    all_fg = {p.get("foreground", "").lower() for p in text_pairs}
    all_bg = {p.get("background", "").lower() for p in text_pairs}
    all_btn = {b.get("background_color", "").lower() for b in buttons}

    all_colors = (all_fg | all_bg | all_btn) - {"", "#ffffff", "#000000", "#fff", "#000"}

    if len(all_colors) > 8:
        issues.append(Issue(
            rule_id="DS5_colour_palette_sprawl",
            category=Category.CONSISTENCY,
            severity=Severity.MEDIUM,
            confidence=0.7,
            message=(
                f"{len(all_colors)} distinct colours detected across the UI — "
                "no bounded palette in use."
            ),
            recommendation=(
                "Define a palette of 6–10 named colours (brand, neutral, semantic) "
                "as CSS variables and use only those values."
            ),
            evidence=f"Colours (sample): {', '.join(sorted(all_colors)[:8])}",
            estimated_time="3 hours",
            why=(
                "Colour sprawl makes the UI feel inconsistent and multiplies the "
                "cost of rebranding. Products like Stripe and Linear use a palette "
                "of < 10 intentional colours — everything else is a tint or shade "
                "computed from those base values."
            ),
            references=["Stripe", "Tailwind CSS colour palette", "Radix UI Colors"],
        ))

    return issues


# ── card consistency ──────────────────────────────────────────────────────────

def _check_card_consistency(parsed_page: dict) -> list[Issue]:
    issues: list[Issue] = []
    cards = parsed_page.get("cards", [])
    if len(cards) < 2:
        return issues

    paddings = [
        min(c.get("padding_top_px", 0), c.get("padding_right_px", 0),
            c.get("padding_bottom_px", 0), c.get("padding_left_px", 0))
        for c in cards
    ]
    if paddings and (max(paddings) - min(paddings)) > 8:
        issues.append(Issue(
            rule_id="DS6_card_padding_inconsistency",
            category=Category.CONSISTENCY,
            severity=Severity.LOW,
            confidence=0.75,
            message=(
                f"Card padding ranges from {min(paddings):.0f}px to {max(paddings):.0f}px "
                "— no shared card token."
            ),
            recommendation=(
                "Standardise card padding via --card-padding CSS variable. "
                "One size (e.g. 24px) works for 90% of cards."
            ),
            evidence=f"Card padding values: {[round(p) for p in paddings]}",
            estimated_time="15 minutes",
            why=(
                "Cards with different internal padding feel like different component "
                "libraries mixed together. A single --card-padding token eliminates "
                "inconsistency and makes the layout breathe uniformly."
            ),
            references=["Notion", "Linear", "Stripe"],
        ))

    return issues
