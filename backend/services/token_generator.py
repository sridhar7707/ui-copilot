"""
Module 12 — Design Token Generator.

Produces a complete CSS custom-property token file covering:
  • Color palette + semantic aliases
  • Spacing scale (8pt grid)
  • Border-radius scale
  • Elevation / shadow scale
  • Typography scale (size, weight, line-height, letter-spacing)
  • Animation / transition tokens
  • Dark-mode overrides (via @media prefers-color-scheme)

Unlike Module 10 (which generates targeted fix blocks),
this module outputs a full, standalone token file that can be
dropped into any project as a design-system foundation.
"""
from __future__ import annotations

from backend.models.analysis import AnalysisResult
from backend.utils.config_loader import load_scoring_config


def generate(result: AnalysisResult) -> str:
    """Return a complete CSS token file derived from the analysis."""
    cfg = load_scoring_config()["thresholds"]
    lines: list[str] = []

    lines += [
        "/*",
        " * UICopilot — Generated Design Tokens (Module 12)",
        f" * Overall score: {result.overall_score}/100",
        " *",
        " * Drop this file into your project and import it before all other CSS.",
        " * Tokens follow the format: --{category}-{variant}-{property}",
        " */",
        "",
    ]

    lines += _color_tokens(result)
    lines += _spacing_tokens(cfg)
    lines += _radius_tokens()
    lines += _elevation_tokens()
    lines += _typography_tokens(cfg)
    lines += _animation_tokens()
    lines += _dark_mode_tokens()

    return "\n".join(lines)


# ── section builders ──────────────────────────────────────────────────────────

def _color_tokens(result: AnalysisResult) -> list[str]:
    ids = {i.rule_id for i in result.issues}

    # Pick a safe primary if contrast issues exist
    primary = "#005fcc" if "C1_wcag_aa_contrast" in ids else "#0066ff"

    return [
        "/* ─── Colors ─────────────────────────────────────────── */",
        ":root {",
        "  /* Primitive palette */",
        f"  --color-blue-50:  #eff6ff;",
        f"  --color-blue-100: #dbeafe;",
        f"  --color-blue-500: {primary};",
        f"  --color-blue-600: #0050b3;",
        f"  --color-blue-700: #003d87;",
        "",
        "  --color-gray-50:  #f9fafb;",
        "  --color-gray-100: #f3f4f6;",
        "  --color-gray-200: #e5e7eb;",
        "  --color-gray-300: #d1d5db;",
        "  --color-gray-500: #6b7280;",
        "  --color-gray-700: #374151;",
        "  --color-gray-900: #111827;",
        "",
        "  --color-green-500: #16a34a;",
        "  --color-red-500:   #dc2626;",
        "  --color-yellow-500:#d97706;",
        "",
        "  /* Semantic aliases */",
        "  --color-primary:         var(--color-blue-500);",
        "  --color-primary-hover:   var(--color-blue-600);",
        "  --color-primary-active:  var(--color-blue-700);",
        "  --color-primary-subtle:  var(--color-blue-50);",
        "",
        "  --color-surface:         #ffffff;",
        "  --color-surface-raised:  var(--color-gray-50);",
        "  --color-surface-overlay: var(--color-gray-100);",
        "",
        "  --color-border:          var(--color-gray-200);",
        "  --color-border-strong:   var(--color-gray-300);",
        "",
        "  --color-text-primary:    var(--color-gray-900);",
        "  --color-text-secondary:  var(--color-gray-700);",
        "  --color-text-muted:      var(--color-gray-500);",
        "  --color-text-inverse:    #ffffff;",
        "",
        "  --color-success: var(--color-green-500);",
        "  --color-danger:  var(--color-red-500);",
        "  --color-warning: var(--color-yellow-500);",
        "}",
        "",
    ]


def _spacing_tokens(cfg: dict) -> list[str]:
    base = cfg["spacing"]["grid_base_px"]
    multiples = [0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16]
    lines = [
        "/* ─── Spacing (8pt grid) ──────────────────────────────── */",
        ":root {",
    ]
    for m in multiples:
        val = int(base * m)
        name = f"{val}" if val == int(val) else str(val)
        lines.append(f"  --space-{name}: {val}px;")
    lines += [
        "  /* Semantic spacing aliases */",
        "  --space-page-x:    var(--space-24);",
        "  --space-page-y:    var(--space-32);",
        "  --space-section:   var(--space-48);",
        "  --space-component: var(--space-16);",
        "  --space-element:   var(--space-8);",
        "}",
        "",
    ]
    return lines


def _radius_tokens() -> list[str]:
    return [
        "/* ─── Border radius ───────────────────────────────────── */",
        ":root {",
        "  --radius-none: 0px;",
        "  --radius-sm:   4px;",
        "  --radius-md:   6px;",
        "  --radius-lg:   8px;",
        "  --radius-xl:   12px;",
        "  --radius-2xl:  16px;",
        "  --radius-full: 9999px;",
        "  /* Semantic aliases */",
        "  --radius-button: var(--radius-md);",
        "  --radius-card:   var(--radius-lg);",
        "  --radius-input:  var(--radius-sm);",
        "  --radius-badge:  var(--radius-full);",
        "}",
        "",
    ]


def _elevation_tokens() -> list[str]:
    return [
        "/* ─── Elevation / shadows ─────────────────────────────── */",
        ":root {",
        "  --shadow-none: none;",
        "  --shadow-xs:   0 1px 2px 0 rgb(0 0 0 / 0.05);",
        "  --shadow-sm:   0 1px 3px 0 rgb(0 0 0 / 0.10), 0 1px 2px -1px rgb(0 0 0 / 0.10);",
        "  --shadow-md:   0 4px 6px -1px rgb(0 0 0 / 0.10), 0 2px 4px -2px rgb(0 0 0 / 0.10);",
        "  --shadow-lg:   0 10px 15px -3px rgb(0 0 0 / 0.10), 0 4px 6px -4px rgb(0 0 0 / 0.10);",
        "  --shadow-xl:   0 20px 25px -5px rgb(0 0 0 / 0.10), 0 8px 10px -6px rgb(0 0 0 / 0.10);",
        "  /* Semantic aliases */",
        "  --shadow-card:    var(--shadow-sm);",
        "  --shadow-dialog:  var(--shadow-xl);",
        "  --shadow-tooltip: var(--shadow-md);",
        "  --shadow-focus:   0 0 0 3px rgb(0 95 204 / 0.35);",
        "}",
        "",
    ]


def _typography_tokens(cfg: dict) -> list[str]:
    t = cfg["typography"]
    body_px = t["recommended_body_size_px"]
    lh = t["line_height_min"]
    min_h = t["min_heading_size_px"]

    return [
        "/* ─── Typography ──────────────────────────────────────── */",
        ":root {",
        "  /* Font families */",
        '  --font-sans:  system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;',
        '  --font-mono:  ui-monospace, "Cascadia Code", "Fira Code", monospace;',
        "",
        "  /* Size scale */",
        f"  --text-xs:   {max(10, body_px - 4)}px;",
        f"  --text-sm:   {max(12, body_px - 2)}px;",
        f"  --text-base: {body_px}px;",
        f"  --text-lg:   {body_px + 2}px;",
        f"  --text-xl:   {int(min_h * 1.0)}px;",
        f"  --text-2xl:  {int(min_h * 1.15)}px;",
        f"  --text-3xl:  {int(min_h * 1.4)}px;",
        f"  --text-4xl:  {int(min_h * 1.8)}px;",
        "",
        "  /* Weight scale */",
        "  --font-weight-normal:    400;",
        "  --font-weight-medium:    500;",
        "  --font-weight-semibold:  600;",
        "  --font-weight-bold:      700;",
        "",
        "  /* Line height */",
        f"  --leading-none:   1.0;",
        f"  --leading-tight:  1.25;",
        f"  --leading-snug:   1.375;",
        f"  --leading-normal: {lh};",
        f"  --leading-relaxed:1.625;",
        "",
        "  /* Letter spacing */",
        "  --tracking-tight:  -0.025em;",
        "  --tracking-normal:  0em;",
        "  --tracking-wide:    0.025em;",
        "  --tracking-wider:   0.05em;",
        "  --tracking-widest:  0.1em;",
        "",
        "  /* Semantic aliases */",
        "  --font-body:          var(--font-sans);",
        "  --font-size-body:     var(--text-base);",
        "  --font-size-label:    var(--text-sm);",
        "  --font-size-caption:  var(--text-xs);",
        "  --line-height-body:   var(--leading-normal);",
        "}",
        "",
    ]


def _animation_tokens() -> list[str]:
    return [
        "/* ─── Animation & transitions ─────────────────────────── */",
        ":root {",
        "  /* Durations */",
        "  --duration-instant: 50ms;",
        "  --duration-fast:    100ms;",
        "  --duration-normal:  200ms;",
        "  --duration-slow:    300ms;",
        "  --duration-slower:  500ms;",
        "",
        "  /* Easing */",
        "  --ease-default:    cubic-bezier(0.4, 0, 0.2, 1);",
        "  --ease-in:         cubic-bezier(0.4, 0, 1, 1);",
        "  --ease-out:        cubic-bezier(0, 0, 0.2, 1);",
        "  --ease-in-out:     cubic-bezier(0.4, 0, 0.2, 1);",
        "  --ease-spring:     cubic-bezier(0.34, 1.56, 0.64, 1);",
        "",
        "  /* Semantic shorthands */",
        "  --transition-colors: color var(--duration-normal) var(--ease-default),",
        "                        background-color var(--duration-normal) var(--ease-default),",
        "                        border-color var(--duration-normal) var(--ease-default);",
        "  --transition-opacity:  opacity var(--duration-normal) var(--ease-default);",
        "  --transition-transform: transform var(--duration-normal) var(--ease-default);",
        "  --transition-shadow:   box-shadow var(--duration-normal) var(--ease-default);",
        "}",
        "",
    ]


def _dark_mode_tokens() -> list[str]:
    return [
        "/* ─── Dark mode overrides ─────────────────────────────── */",
        "@media (prefers-color-scheme: dark) {",
        "  :root {",
        "    --color-surface:         #0f172a;",
        "    --color-surface-raised:  #1e293b;",
        "    --color-surface-overlay: #334155;",
        "",
        "    --color-border:          #1e293b;",
        "    --color-border-strong:   #334155;",
        "",
        "    --color-text-primary:    #f8fafc;",
        "    --color-text-secondary:  #cbd5e1;",
        "    --color-text-muted:      #94a3b8;",
        "",
        "    --color-primary:         #60a5fa;",
        "    --color-primary-hover:   #93c5fd;",
        "    --color-primary-active:  #bfdbfe;",
        "    --color-primary-subtle:  #1e3a5f;",
        "  }",
        "}",
    ]
