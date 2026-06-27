"""
Module 20 — Component Library.

Aggregates component snapshots from multiple page analyses into a
project-level component library: buttons, cards, inputs, typography,
colors, and spacing patterns.

Pure function — no DB access, no IO.
"""
from __future__ import annotations


def build(analyses: list[dict]) -> dict:
    """
    Aggregate component data across all pages in a project.

    Each dict in ``analyses`` is a parsed ``result_json`` from
    ``analysis_repo.latest_for_page``.  Analyses that were saved without
    a component snapshot (i.e. older analyses or the stateless /analyze
    endpoint) are counted toward ``total_pages`` but skipped for component
    aggregation.

    Returns::

        {
            "coverage": {"total_pages": int, "pages_with_components": int},
            "buttons": {"total_detected": int, "background_colors": list,
                        "border_radii_px": list, "font_sizes_px": list,
                        "style_count": int},
            "cards": {"total_detected": int, "padding_values_px": list,
                      "border_radii_px": list},
            "inputs": {"total_detected": int},
            "typography": {"fonts": list, "body_font_sizes_px": list},
            "spacing": {"values_px": list, "on_8pt_grid": bool | None},
            "colors": {"text_background_pairs": list},
        }
    """
    with_data = [a for a in analyses if a.get("components")]

    # ── buttons ──────────────────────────────────────────────────────────────
    all_buttons: list[dict] = []
    for a in with_data:
        all_buttons.extend(a["components"].get("buttons", []))

    bg_colors = sorted({
        b["background_color"].lower()
        for b in all_buttons
        if b.get("background_color")
    })
    btn_radii = sorted({
        b["border_radius_px"]
        for b in all_buttons
        if b.get("border_radius_px") is not None
    })
    btn_font_sizes = sorted({
        b["font_size_px"]
        for b in all_buttons
        if b.get("font_size_px") is not None
    })

    # ── cards ─────────────────────────────────────────────────────────────────
    all_cards: list[dict] = []
    for a in with_data:
        all_cards.extend(a["components"].get("cards", []))

    card_paddings = sorted({
        c["padding_px"]
        for c in all_cards
        if c.get("padding_px") is not None
    })
    card_radii = sorted({
        c["border_radius_px"]
        for c in all_cards
        if c.get("border_radius_px") is not None
    })

    # ── inputs ────────────────────────────────────────────────────────────────
    all_inputs: list[dict] = []
    for a in with_data:
        all_inputs.extend(a["components"].get("inputs", []))

    # ── typography ────────────────────────────────────────────────────────────
    all_fonts: set[str] = set()
    body_sizes: set[float] = set()
    for a in with_data:
        for f in a["components"].get("fonts", []):
            if isinstance(f, str):
                all_fonts.add(f)
            elif isinstance(f, dict) and f.get("family"):
                all_fonts.add(f["family"])
        size = a["components"].get("body_font_size_px")
        if size is not None:
            body_sizes.add(float(size))

    # ── spacing ───────────────────────────────────────────────────────────────
    all_spacing: list[float] = []
    for a in with_data:
        all_spacing.extend(
            float(v)
            for v in a["components"].get("spacing_values_px", [])
            if v is not None
        )
    spacing_values = sorted(set(all_spacing))

    on_grid: bool | None = None
    positives = [v for v in spacing_values if v > 0]
    if positives:
        on_grid = all(v % 4 == 0 for v in positives)

    # ── colors ────────────────────────────────────────────────────────────────
    color_pairs: list[dict] = []
    seen: set[tuple] = set()
    for a in with_data:
        for pair in a["components"].get("text_color_pairs", []):
            key = (pair.get("text_color", ""), pair.get("background_color", ""))
            if key not in seen:
                seen.add(key)
                color_pairs.append(pair)

    return {
        "coverage": {
            "total_pages": len(analyses),
            "pages_with_components": len(with_data),
        },
        "buttons": {
            "total_detected": len(all_buttons),
            "background_colors": bg_colors,
            "border_radii_px": btn_radii,
            "font_sizes_px": btn_font_sizes,
            "style_count": len(bg_colors),
        },
        "cards": {
            "total_detected": len(all_cards),
            "padding_values_px": list(card_paddings),
            "border_radii_px": list(card_radii),
        },
        "inputs": {
            "total_detected": len(all_inputs),
        },
        "typography": {
            "fonts": sorted(all_fonts),
            "body_font_sizes_px": sorted(body_sizes),
        },
        "spacing": {
            "values_px": spacing_values,
            "on_8pt_grid": on_grid,
        },
        "colors": {
            "text_background_pairs": color_pairs[:20],
        },
    }
