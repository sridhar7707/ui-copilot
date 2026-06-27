"""
Module 10 — CSS Generator.

Generates CSS variables (design tokens) and targeted fix blocks from an
AnalysisResult.  No API calls — pure text generation from the parsed data
and detected issues.
"""
from __future__ import annotations

from backend.models.analysis import AnalysisResult
from backend.utils.config_loader import load_scoring_config


def generate(result: AnalysisResult) -> str:
    """Return a ready-to-paste CSS snippet from an AnalysisResult."""
    cfg = load_scoring_config()["thresholds"]
    lines: list[str] = []

    lines.append("/* ============================================================")
    lines.append("   UICopilot — Generated CSS Fixes")
    lines.append(f"   Overall score: {result.overall_score}/100")
    lines.append("   Copy relevant blocks into your stylesheet.")
    lines.append("   ============================================================ */")
    lines.append("")

    _append_tokens(lines, result, cfg)
    _append_typography_fixes(lines, result, cfg)
    _append_spacing_fixes(lines, result, cfg)
    _append_button_fixes(lines, result, cfg)
    _append_form_fixes(lines, result, cfg)
    _append_table_fixes(lines, result, cfg)

    return "\n".join(lines)


# ── section builders ──────────────────────────────────────────────────────────

def _append_tokens(lines: list[str], result: AnalysisResult, cfg: dict) -> None:
    t_sp = cfg["spacing"]
    base = t_sp["grid_base_px"]
    lines.append("/* === Design Tokens === */")
    lines.append(":root {")
    lines.append(f"  /* Spacing scale ({base}pt grid) */")
    for mult in (0.5, 1, 1.5, 2, 3, 4, 6):
        val = int(base * mult)
        lines.append(f"  --space-{val}: {val}px;")
    lines.append("")

    # Typography tokens
    t_ty = cfg["typography"]
    lines.append("  /* Typography */")
    lines.append(f"  --font-size-body: {t_ty['recommended_body_size_px']}px;")
    lines.append(f"  --line-height-body: {t_ty['line_height_min']};")
    lines.append("  --font-family-body: system-ui, -apple-system, sans-serif;")
    lines.append("  --font-family-mono: ui-monospace, 'Cascadia Code', monospace;")
    lines.append("")

    # Button tokens
    t_bt = cfg["buttons"]
    t_sp2 = cfg["spacing"]
    lines.append("  /* Buttons */")
    lines.append(f"  --btn-padding-y: {t_sp2['button_min_padding_y_px']}px;")
    lines.append(f"  --btn-padding-x: {t_sp2['button_min_padding_x_px']}px;")
    lines.append(f"  --btn-min-height: {t_bt['min_touch_target_px']}px;")
    lines.append("  --btn-radius: 6px;")
    lines.append("  --btn-primary-bg: #005fcc;")
    lines.append("  --btn-primary-color: #ffffff;")
    lines.append("  --btn-focus-outline: 2px solid #005fcc;")
    lines.append("  --btn-focus-offset: 2px;")
    lines.append("")

    # Card tokens
    t_cards = cfg["spacing"]
    lines.append("  /* Cards */")
    lines.append(f"  --card-padding: {t_cards['card_min_padding_px']}px;")
    lines.append("  --card-radius: 8px;")
    lines.append("  --card-border: 1px solid #e5e7eb;")
    lines.append("}")
    lines.append("")


def _append_typography_fixes(lines: list[str], result: AnalysisResult, cfg: dict) -> None:
    issues_by_id = {i.rule_id for i in result.issues}
    if not any(r in issues_by_id for r in ("T1_body_font_size", "T2_font_family_count",
                                            "T3_line_height", "T4_heading_hierarchy",
                                            "T5_heading_size")):
        return

    t = cfg["typography"]
    lines.append("/* === Typography Fixes === */")
    if "T1_body_font_size" in issues_by_id or "T3_line_height" in issues_by_id:
        lines.append("body, p, li, td, th {")
        lines.append("  font-size: var(--font-size-body);")
        lines.append("  line-height: var(--line-height-body);")
        lines.append("  font-family: var(--font-family-body);")
        lines.append("}")
        lines.append("")

    if "T4_heading_hierarchy" in issues_by_id or "T5_heading_size" in issues_by_id:
        min_h = t["min_heading_size_px"]
        lines.append(f"h1 {{ font-size: {int(min_h * 1.8)}px; font-weight: 700; }}")
        lines.append(f"h2 {{ font-size: {int(min_h * 1.4)}px; font-weight: 600; }}")
        lines.append(f"h3 {{ font-size: {int(min_h * 1.15)}px; font-weight: 600; }}")
        lines.append("")


def _append_spacing_fixes(lines: list[str], result: AnalysisResult, cfg: dict) -> None:
    issues_by_id = {i.rule_id for i in result.issues}
    if not any(r in issues_by_id for r in ("S1_button_padding", "S2_card_padding",
                                            "S3_off_grid_spacing")):
        return

    lines.append("/* === Spacing Fixes === */")
    if "S2_card_padding" in issues_by_id:
        lines.append(".card, [class*='card'] {")
        lines.append("  padding: var(--card-padding);")
        lines.append("  border-radius: var(--card-radius);")
        lines.append("  border: var(--card-border);")
        lines.append("}")
        lines.append("")


def _append_button_fixes(lines: list[str], result: AnalysisResult, cfg: dict) -> None:
    issues_by_id = {i.rule_id for i in result.issues}
    if not any(r in issues_by_id for r in ("S1_button_padding", "B1_button_style_count",
                                            "B2_border_radius_variance", "B3_focus_style",
                                            "B4_touch_target")):
        return

    lines.append("/* === Button Fixes === */")
    lines.append("button, [type='button'], [type='submit'], .btn {")
    lines.append("  padding: var(--btn-padding-y) var(--btn-padding-x);")
    lines.append("  min-height: var(--btn-min-height);")
    lines.append("  border-radius: var(--btn-radius);")
    lines.append("  font-size: var(--font-size-body);")
    lines.append("  cursor: pointer;")
    lines.append("}")
    lines.append("")
    if "B3_focus_style" in issues_by_id:
        lines.append("button:focus-visible,")
        lines.append("[type='button']:focus-visible,")
        lines.append("[type='submit']:focus-visible,")
        lines.append(".btn:focus-visible {")
        lines.append("  outline: var(--btn-focus-outline);")
        lines.append("  outline-offset: var(--btn-focus-offset);")
        lines.append("}")
        lines.append("")
    if "B1_button_style_count" in issues_by_id:
        lines.append(".btn-primary {")
        lines.append("  background: var(--btn-primary-bg);")
        lines.append("  color: var(--btn-primary-color);")
        lines.append("  border: none;")
        lines.append("}")
        lines.append("")
        lines.append(".btn-secondary {")
        lines.append("  background: transparent;")
        lines.append("  color: var(--btn-primary-bg);")
        lines.append("  border: 1px solid var(--btn-primary-bg);")
        lines.append("}")
        lines.append("")


def _append_form_fixes(lines: list[str], result: AnalysisResult, cfg: dict) -> None:
    issues_by_id = {i.rule_id for i in result.issues}
    if not any(r in issues_by_id for r in ("F1_missing_label", "F2_placeholder_as_label",
                                            "F3_input_padding")):
        return

    t = cfg["forms"]
    lines.append("/* === Form Fixes === */")
    lines.append("label {")
    lines.append("  display: block;")
    lines.append("  font-size: var(--font-size-body);")
    lines.append("  font-weight: 500;")
    lines.append("  margin-bottom: 4px;")
    lines.append("}")
    lines.append("")
    if "F3_input_padding" in issues_by_id:
        lines.append("input, select, textarea {")
        lines.append(f"  padding: {t['min_input_padding_px']}px 12px;")
        lines.append("  font-size: var(--font-size-body);")
        lines.append("  border: 1px solid #d1d5db;")
        lines.append("  border-radius: 4px;")
        lines.append("  width: 100%;")
        lines.append("}")
        lines.append("")


def _append_table_fixes(lines: list[str], result: AnalysisResult, cfg: dict) -> None:
    issues_by_id = {i.rule_id for i in result.issues}
    if not any(r in issues_by_id for r in ("TBL1_missing_header", "TBL2_no_zebra",
                                            "TBL3_cell_padding")):
        return

    t = cfg["tables"]
    lines.append("/* === Table Fixes === */")
    lines.append("table { border-collapse: collapse; width: 100%; }")
    lines.append(f"td, th {{ padding: {t['min_cell_padding_px']}px 12px; text-align: left; }}")
    if "TBL1_missing_header" in issues_by_id:
        lines.append("th {")
        lines.append("  font-weight: 600;")
        lines.append("  background: #f3f4f6;")
        lines.append("  border-bottom: 2px solid #e5e7eb;")
        lines.append("}")
        lines.append("")
    if "TBL2_no_zebra" in issues_by_id:
        lines.append("tr:nth-child(even) { background: #f9fafb; }")
        lines.append("")
