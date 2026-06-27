"""
Module 11 — HTML Improvements.

Generates semantic HTML snippets, ARIA fixes, and responsive layout patterns
based on the issues detected in an AnalysisResult.  No API calls — pure text
generation from parsed issues.
"""
from __future__ import annotations

from backend.models.analysis import AnalysisResult
from backend.models.issue import Category


def generate(result: AnalysisResult) -> str:
    """Return ready-to-use HTML improvement snippets for the given result."""
    ids = {i.rule_id for i in result.issues}
    a11y_cats = {i.category for i in result.issues}

    sections: list[str] = []

    sections.append(_header(result))
    sections.append(_document_shell(ids))

    if Category.ACCESSIBILITY in a11y_cats or ids & {
        "F1_missing_label", "F2_placeholder_as_label", "B3_focus_style", "B4_touch_target",
        "TBL1_missing_header",
    }:
        sections.append(_skip_link())

    if "F1_missing_label" in ids or "F2_placeholder_as_label" in ids:
        sections.append(_form_patterns(ids))

    if "TBL1_missing_header" in ids:
        sections.append(_table_pattern())

    if "B4_touch_target" in ids or "B1_button_style_count" in ids:
        sections.append(_button_pattern(ids))

    if "T1_body_font_size" in ids or "T4_heading_hierarchy" in ids or "T5_heading_size" in ids:
        sections.append(_typography_pattern())

    sections.append(_landmark_roles(ids))
    sections.append(_responsive_meta())

    return "\n\n".join(s for s in sections if s)


# ── section builders ──────────────────────────────────────────────────────────

def _header(result: AnalysisResult) -> str:
    return (
        "<!-- ============================================================\n"
        "     UICopilot — HTML Improvements (Module 11)\n"
        f"     Overall score: {result.overall_score}/100\n"
        "     Apply the snippets below to improve semantic structure,\n"
        "     accessibility, and responsiveness.\n"
        "     ============================================================ -->"
    )


def _document_shell(ids: set[str]) -> str:
    lines = [
        "<!-- 1. Document shell — always include these on every page -->",
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Page Title</title>',
        '</head>',
        '<body>',
        '  <!-- page content -->',
        '</body>',
        '</html>',
        "<!-- lang=\"en\" enables correct screen-reader pronunciation. -->",
        "<!-- viewport meta enables mobile scaling. -->",
    ]
    return "\n".join(lines)


def _skip_link() -> str:
    return (
        "<!-- 2. Skip navigation link — place as the very first child of <body> -->\n"
        '<a class="skip-link" href="#main-content">Skip to main content</a>\n'
        "\n"
        "<!-- Add to your stylesheet:\n"
        "  .skip-link {\n"
        "    position: absolute; top: -100%;\n"
        "    background: #005fcc; color: #fff;\n"
        "    padding: 8px 16px; z-index: 9999;\n"
        "  }\n"
        "  .skip-link:focus { top: 0; }\n"
        "-->"
    )


def _form_patterns(ids: set[str]) -> str:
    lines = ["<!-- 3. Accessible form patterns -->"]

    if "F1_missing_label" in ids:
        lines += [
            "<!-- BEFORE (inaccessible — no label): -->",
            '<!-- <input type="text" placeholder="Email"> -->',
            "",
            "<!-- AFTER (accessible — explicit label): -->",
            '<div class="form-group">',
            '  <label for="email">Email address</label>',
            '  <input type="email" id="email" name="email"',
            '         autocomplete="email" required>',
            "</div>",
            "",
        ]

    if "F2_placeholder_as_label" in ids:
        lines += [
            "<!-- BEFORE (placeholder doubles as label — disappears on type): -->",
            '<!-- <input type="text" placeholder="First name"> -->',
            "",
            "<!-- AFTER (visible label, optional hint via aria-describedby): -->",
            '<div class="form-group">',
            '  <label for="first-name">First name</label>',
            '  <input type="text" id="first-name" name="first_name"',
            '         autocomplete="given-name" placeholder="e.g. Alex">',
            "  <!-- placeholder is now supplementary, not the only label -->",
            "</div>",
            "",
        ]

    lines += [
        "<!-- Error message pattern (screen-reader-friendly): -->",
        '<div class="form-group" aria-describedby="email-error">',
        '  <label for="email2">Email address</label>',
        '  <input type="email" id="email2" aria-invalid="true"',
        '         aria-describedby="email-error">',
        '  <span id="email-error" role="alert" class="error">',
        '    Please enter a valid email address.',
        '  </span>',
        "</div>",
    ]
    return "\n".join(lines)


def _table_pattern() -> str:
    return (
        "<!-- 4. Accessible table pattern -->\n"
        "<!-- BEFORE (no headers — screen readers can't map cells to columns): -->\n"
        "<!-- <table><tr><td>Name</td><td>Value</td></tr></table> -->\n"
        "\n"
        "<!-- AFTER: -->\n"
        '<table>\n'
        '  <caption>Data summary</caption> <!-- describes the table -->\n'
        '  <thead>\n'
        '    <tr>\n'
        '      <th scope="col">Name</th>\n'
        '      <th scope="col">Value</th>\n'
        '      <th scope="col">Status</th>\n'
        '    </tr>\n'
        '  </thead>\n'
        '  <tbody>\n'
        '    <tr>\n'
        '      <td>Example</td>\n'
        '      <td>42</td>\n'
        '      <td><span aria-label="Active">✓</span></td>\n'
        '    </tr>\n'
        '  </tbody>\n'
        '</table>\n'
        '<!-- scope="col" links each header to its column for AT users. -->'
    )


def _button_pattern(ids: set[str]) -> str:
    lines = ["<!-- 5. Button patterns -->"]

    if "B4_touch_target" in ids:
        lines += [
            "<!-- Touch target: minimum 44×44px (WCAG 2.5.8) -->",
            "<!-- Ensure button has min-height/min-width via CSS, not padding alone. -->",
            '<button type="button" class="btn btn-primary">',
            "  Confirm",
            "</button>",
            "<!-- In CSS: .btn { min-height: 44px; padding: 10px 20px; } -->",
            "",
        ]

    if "B1_button_style_count" in ids:
        lines += [
            "<!-- Consolidated button variants — use modifier classes, not one-off styles: -->",
            '<button type="button" class="btn btn-primary">Primary action</button>',
            '<button type="button" class="btn btn-secondary">Secondary action</button>',
            '<button type="button" class="btn btn-danger">Destructive action</button>',
            '<button type="submit" class="btn btn-primary">Submit</button>',
            "",
        ]

    lines += [
        "<!-- Icon-only button — always add aria-label: -->",
        '<button type="button" aria-label="Close dialog">',
        '  <svg aria-hidden="true" focusable="false">…</svg>',
        "</button>",
    ]
    return "\n".join(lines)


def _typography_pattern() -> str:
    return (
        "<!-- 6. Heading hierarchy — one h1 per page, no skipped levels -->\n"
        "<main id=\"main-content\">\n"
        "  <h1>Page title</h1>          <!-- one per page -->\n"
        "\n"
        "  <section aria-labelledby=\"section-1-heading\">\n"
        "    <h2 id=\"section-1-heading\">Section heading</h2>\n"
        "    <p>Body copy at 16px / 1.5 line-height.</p>\n"
        "\n"
        "    <h3>Sub-section heading</h3>\n"
        "    <!-- Never skip from h2 → h4 — breaks outline for AT users. -->\n"
        "  </section>\n"
        "</main>"
    )


def _landmark_roles(ids: set[str]) -> str:
    return (
        "<!-- 7. ARIA landmark roles — helps screen-reader users navigate quickly -->\n"
        "<body>\n"
        '  <header role="banner">\n'
        "    <!-- logo, site nav -->\n"
        "  </header>\n"
        "\n"
        '  <nav aria-label="Primary navigation">\n'
        "    <!-- main links -->\n"
        "  </nav>\n"
        "\n"
        '  <main id="main-content">\n'
        "    <!-- primary page content -->\n"
        "  </main>\n"
        "\n"
        '  <aside aria-label="Sidebar">\n'
        "    <!-- supplementary content -->\n"
        "  </aside>\n"
        "\n"
        '  <footer role="contentinfo">\n'
        "    <!-- copyright, secondary links -->\n"
        "  </footer>\n"
        "</body>"
    )


def _responsive_meta() -> str:
    return (
        "<!-- 8. Responsive layout skeleton -->\n"
        '<div class="layout">\n'
        '  <header class="layout__header">…</header>\n'
        '  <nav class="layout__nav">…</nav>\n'
        '  <main class="layout__main" id="main-content">…</main>\n'
        '  <aside class="layout__aside">…</aside>\n'
        '  <footer class="layout__footer">…</footer>\n'
        "</div>\n"
        "\n"
        "<!--\n"
        "  Responsive CSS (add to stylesheet):\n"
        "  .layout {\n"
        "    display: grid;\n"
        "    grid-template-columns: 240px 1fr;\n"
        "    grid-template-rows: auto 1fr auto;\n"
        "    min-height: 100vh;\n"
        "  }\n"
        "  @media (max-width: 768px) {\n"
        "    .layout { grid-template-columns: 1fr; }\n"
        "    .layout__nav { display: none; } /* replace with mobile nav */\n"
        "  }\n"
        "-->"
    )
