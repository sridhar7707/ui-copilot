"""
Generates the 32 'poor' benchmark metadata JSON files for UICopilot's
Module 3b Benchmark Library (Pack 1).

These pair with AI-generated mockup PNGs of the same id, dropped into
data/benchmarks/images/poor/{category}/{id}.png

Run: python scripts/generate_poor_metadata.py
Output: data/benchmarks/images/poor/{category}/{id}.json
"""

import json
import os

OUTPUT_ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "benchmarks", "images", "poor")

ENTRIES = [
    # ---------------- DASHBOARDS (8) ----------------
    {
        "id": "dashboard_001", "category": "dashboards", "quality_score": 38,
        "style": "cluttered", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "high",
        "components": ["card", "table", "bar_chart", "line_chart", "sidebar", "topbar"],
        "attributes": {"spacing": "cramped", "typography": "inconsistent", "contrast": "poor", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Too many cards competing for attention", "No clear visual hierarchy among metrics", "Charts and tables crammed with no breathing room"]
    },
    {
        "id": "dashboard_002", "category": "dashboards", "quality_score": 42,
        "style": "dense", "industry": "finance", "framework": "unspecified",
        "theme": "dark", "layout": "sidebar", "complexity": "high",
        "components": ["card", "table", "kpi_metric", "sidebar"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "low", "density": "overcrowded"},
        "design_tokens": {"padding": 6, "radius": 2, "shadow": "none", "spacing_unit": 4},
        "notes": ["Dark theme with insufficient contrast on text", "KPI numbers buried among secondary data", "Sidebar nav items too closely packed"]
    },
    {
        "id": "dashboard_003", "category": "dashboards", "quality_score": 35,
        "style": "inconsistent", "industry": "crm", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "high",
        "components": ["card", "table", "pie_chart", "topbar"],
        "attributes": {"spacing": "uneven", "typography": "mixed_fonts", "contrast": "poor", "density": "overcrowded"},
        "design_tokens": {"padding": 8, "radius": 4, "shadow": "heavy", "spacing_unit": 4},
        "notes": ["Multiple unrelated card styles on one screen", "Heavy drop shadows used inconsistently", "Mixed font families across widgets"]
    },
    {
        "id": "dashboard_004", "category": "dashboards", "quality_score": 40,
        "style": "noisy", "industry": "analytics", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "high",
        "components": ["bar_chart", "line_chart", "pie_chart", "table", "card"],
        "attributes": {"spacing": "cramped", "typography": "inconsistent", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 6, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Too many chart types on a single view", "No grouping or section headers to organize content", "Colors clash across adjacent charts"]
    },
    {
        "id": "dashboard_005", "category": "dashboards", "quality_score": 31,
        "style": "overloaded", "industry": "ai_saas", "framework": "unspecified",
        "theme": "dark", "layout": "grid", "complexity": "high",
        "components": ["card", "table", "kpi_metric", "line_chart", "sidebar", "topbar"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "low", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Every available widget type used at once", "No empty space anywhere on the screen", "Primary metric has no visual emphasis over secondary ones"]
    },
    {
        "id": "dashboard_006", "category": "dashboards", "quality_score": 44,
        "style": "misaligned", "industry": "finance", "framework": "unspecified",
        "theme": "light", "layout": "sidebar", "complexity": "medium",
        "components": ["card", "table", "line_chart"],
        "attributes": {"spacing": "uneven", "typography": "inconsistent", "contrast": "medium", "density": "moderate"},
        "design_tokens": {"padding": 10, "radius": 6, "shadow": "medium", "spacing_unit": 6},
        "notes": ["Cards in the same row have different heights", "Inconsistent left/right alignment across sections", "Chart axis labels overlap"]
    },
    {
        "id": "dashboard_007", "category": "dashboards", "quality_score": 33,
        "style": "low_contrast", "industry": "crm", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "high",
        "components": ["card", "table", "bar_chart", "topbar"],
        "attributes": {"spacing": "cramped", "typography": "low_contrast", "contrast": "poor", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Light gray text on white background throughout", "Status indicators indistinguishable by color alone", "No focal point on the page"]
    },
    {
        "id": "dashboard_008", "category": "dashboards", "quality_score": 29,
        "style": "chaotic", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "high",
        "components": ["card", "table", "pie_chart", "bar_chart", "kpi_metric", "sidebar", "topbar"],
        "attributes": {"spacing": "cramped", "typography": "mixed_fonts", "contrast": "poor", "density": "overcrowded"},
        "design_tokens": {"padding": 2, "radius": 0, "shadow": "heavy", "spacing_unit": 2},
        "notes": ["Random mix of border radii across components", "No consistent color system for status/category coding", "Scrollable area with no clear end or summary"]
    },
    # ---------------- CARDS (4) ----------------
    {
        "id": "cards_001", "category": "cards", "quality_score": 40,
        "style": "inconsistent", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "low",
        "components": ["card"],
        "attributes": {"spacing": "cramped", "typography": "inconsistent", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 6, "radius": 0, "shadow": "none", "spacing_unit": 4},
        "notes": ["Six different card styles shown side by side", "Inconsistent padding between cards", "No shared corner radius or shadow treatment"]
    },
    {
        "id": "cards_002", "category": "cards", "quality_score": 36,
        "style": "cramped", "industry": "finance", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "low",
        "components": ["card", "kpi_metric"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 2, "shadow": "none", "spacing_unit": 2},
        "notes": ["Metric value and label nearly touching", "No visual separation between adjacent cards", "Trend indicator color barely visible"]
    },
    {
        "id": "cards_003", "category": "cards", "quality_score": 33,
        "style": "heavy_shadow", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "grid", "complexity": "low",
        "components": ["card"],
        "attributes": {"spacing": "uneven", "typography": "inconsistent", "contrast": "low", "density": "moderate"},
        "design_tokens": {"padding": 8, "radius": 16, "shadow": "heavy", "spacing_unit": 4},
        "notes": ["Overly heavy drop shadows make cards feel like they're floating awkwardly", "Excessive border radius looks dated", "Text contrast against card background is weak"]
    },
    {
        "id": "cards_004", "category": "cards", "quality_score": 45,
        "style": "flat_no_hierarchy", "industry": "crm", "framework": "unspecified",
        "theme": "dark", "layout": "grid", "complexity": "low",
        "components": ["card"],
        "attributes": {"spacing": "moderate", "typography": "no_hierarchy", "contrast": "medium", "density": "moderate"},
        "design_tokens": {"padding": 12, "radius": 4, "shadow": "none", "spacing_unit": 4},
        "notes": ["Title and value rendered at the same font size", "No clear primary action within the card", "Icon and text alignment is off-center"]
    },
    # ---------------- TABLES (4) ----------------
    {
        "id": "tables_001", "category": "tables", "quality_score": 37,
        "style": "dense", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "full_width", "complexity": "high",
        "components": ["table"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 2, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Row height too small for comfortable scanning", "Header row not visually distinct from data rows", "Too many columns crammed without horizontal scroll affordance"]
    },
    {
        "id": "tables_002", "category": "tables", "quality_score": 41,
        "style": "low_contrast_header", "industry": "crm", "framework": "unspecified",
        "theme": "light", "layout": "full_width", "complexity": "medium",
        "components": ["table"],
        "attributes": {"spacing": "cramped", "typography": "low_contrast", "contrast": "poor", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Header text barely darker than data rows", "No zebra striping or row separation, hard to track across", "Status column uses color alone with no text label"]
    },
    {
        "id": "tables_003", "category": "tables", "quality_score": 34,
        "style": "misaligned_columns", "industry": "finance", "framework": "unspecified",
        "theme": "light", "layout": "full_width", "complexity": "high",
        "components": ["table"],
        "attributes": {"spacing": "uneven", "typography": "inconsistent", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Numeric columns left-aligned instead of right-aligned", "Column widths don't match content, causing wrapping", "Action buttons inconsistently placed per row"]
    },
    {
        "id": "tables_004", "category": "tables", "quality_score": 39,
        "style": "no_empty_state", "industry": "generic", "framework": "unspecified",
        "theme": "dark", "layout": "full_width", "complexity": "medium",
        "components": ["table"],
        "attributes": {"spacing": "cramped", "typography": "inconsistent", "contrast": "low", "density": "moderate"},
        "design_tokens": {"padding": 6, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Empty table shows a blank white area with no message", "Sort indicators on headers are unclear", "Pagination controls visually disconnected from the table"]
    },
    # ---------------- FORMS (4) ----------------
    {
        "id": "forms_001", "category": "forms", "quality_score": 35,
        "style": "cramped_labels", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "single_column", "complexity": "medium",
        "components": ["form", "input", "button"],
        "attributes": {"spacing": "cramped", "typography": "inconsistent", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Labels sit directly on top of inputs with no gap", "No visible focus state on input fields", "Submit button styled identically to a secondary link"]
    },
    {
        "id": "forms_002", "category": "forms", "quality_score": 32,
        "style": "no_validation_feedback", "industry": "saas_signup", "framework": "unspecified",
        "theme": "light", "layout": "single_column", "complexity": "medium",
        "components": ["form", "input", "button"],
        "attributes": {"spacing": "moderate", "typography": "inconsistent", "contrast": "poor", "density": "moderate"},
        "design_tokens": {"padding": 8, "radius": 4, "shadow": "none", "spacing_unit": 4},
        "notes": ["Error states shown only as red border with no message", "Required-field indicators inconsistent across inputs", "Password field has no show/hide toggle"]
    },
    {
        "id": "forms_003", "category": "forms", "quality_score": 30,
        "style": "checkout_overload", "industry": "ecommerce", "framework": "unspecified",
        "theme": "light", "layout": "two_column", "complexity": "high",
        "components": ["form", "input", "button", "card"],
        "attributes": {"spacing": "cramped", "typography": "mixed_fonts", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Too many fields visible at once with no grouping", "Primary CTA button competes visually with secondary buttons", "No progress indicator for a multi-step checkout"]
    },
    {
        "id": "forms_004", "category": "forms", "quality_score": 38,
        "style": "inconsistent_inputs", "industry": "generic", "framework": "unspecified",
        "theme": "dark", "layout": "single_column", "complexity": "low",
        "components": ["form", "input", "button"],
        "attributes": {"spacing": "uneven", "typography": "inconsistent", "contrast": "low", "density": "moderate"},
        "design_tokens": {"padding": 6, "radius": 2, "shadow": "none", "spacing_unit": 4},
        "notes": ["Input field heights vary across the same form", "Placeholder text used in place of actual labels", "Dark theme input borders nearly invisible"]
    },
    # ---------------- NAVIGATION (4) ----------------
    {
        "id": "navigation_001", "category": "navigation", "quality_score": 36,
        "style": "confusing_sidebar", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "sidebar", "complexity": "high",
        "components": ["sidebar", "nav_item"],
        "attributes": {"spacing": "cramped", "typography": "inconsistent", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["No grouping between primary and secondary nav items", "Active state indistinguishable from hover state", "Icons inconsistent in style across items"]
    },
    {
        "id": "navigation_002", "category": "navigation", "quality_score": 41,
        "style": "overcrowded_topnav", "industry": "saas", "framework": "unspecified",
        "theme": "light", "layout": "topnav", "complexity": "high",
        "components": ["topbar", "nav_item"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Too many top-level nav items with no overflow menu", "Logo and nav items crammed together with no breathing room", "Search bar squeezed into remaining space, too narrow to use"]
    },
    {
        "id": "navigation_003", "category": "navigation", "quality_score": 33,
        "style": "no_active_state", "industry": "generic", "framework": "unspecified",
        "theme": "dark", "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "nav_item"],
        "attributes": {"spacing": "moderate", "typography": "inconsistent", "contrast": "low", "density": "moderate"},
        "design_tokens": {"padding": 8, "radius": 0, "shadow": "none", "spacing_unit": 4},
        "notes": ["No visual indication of which page is currently active", "Nested nav items not visually indented", "Collapse/expand icon ambiguous in meaning"]
    },
    {
        "id": "navigation_004", "category": "navigation", "quality_score": 39,
        "style": "inconsistent_icons", "industry": "crm", "framework": "unspecified",
        "theme": "light", "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "nav_item", "topbar"],
        "attributes": {"spacing": "uneven", "typography": "mixed_fonts", "contrast": "medium", "density": "moderate"},
        "design_tokens": {"padding": 6, "radius": 2, "shadow": "none", "spacing_unit": 4},
        "notes": ["Icon set mixes outlined and filled styles inconsistently", "Spacing between nav items varies down the list", "User avatar menu has no visible affordance that it's clickable"]
    },
    # ---------------- CHARTS (2) ----------------
    {
        "id": "charts_001", "category": "charts", "quality_score": 34,
        "style": "unreadable", "industry": "analytics", "framework": "unspecified",
        "theme": "light", "layout": "card", "complexity": "medium",
        "components": ["line_chart"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "poor", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Too many data series plotted on one chart with similar colors", "Axis labels overlapping and unreadable at default zoom", "No legend to identify which line represents what"]
    },
    {
        "id": "charts_002", "category": "charts", "quality_score": 30,
        "style": "misleading_scale", "industry": "finance", "framework": "unspecified",
        "theme": "dark", "layout": "card", "complexity": "low",
        "components": ["pie_chart"],
        "attributes": {"spacing": "moderate", "typography": "low_contrast", "contrast": "poor", "density": "moderate"},
        "design_tokens": {"padding": 8, "radius": 4, "shadow": "none", "spacing_unit": 4},
        "notes": ["Pie slices use near-identical colors, hard to distinguish", "Percentage labels rendered in low-contrast gray on dark background", "Chart title is smaller than the data labels inside it"]
    },
    # ---------------- METRICS (2) ----------------
    {
        "id": "metrics_001", "category": "metrics", "quality_score": 37,
        "style": "no_emphasis", "industry": "saas", "framework": "unspecified",
        "theme": "light", "layout": "card", "complexity": "low",
        "components": ["kpi_metric"],
        "attributes": {"spacing": "cramped", "typography": "no_hierarchy", "contrast": "medium", "density": "moderate"},
        "design_tokens": {"padding": 6, "radius": 0, "shadow": "none", "spacing_unit": 4},
        "notes": ["Primary metric value rendered at the same size as the label", "Trend arrow color doesn't clearly indicate positive or negative", "No comparison period shown for context"]
    },
    {
        "id": "metrics_002", "category": "metrics", "quality_score": 33,
        "style": "buried_kpi", "industry": "finance", "framework": "unspecified",
        "theme": "dark", "layout": "card", "complexity": "medium",
        "components": ["kpi_metric", "sparkline"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "low", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Sparkline overlaps the metric value text", "Secondary stats given equal visual weight to the headline number", "Low contrast makes the metric hard to read at a glance"]
    },
    # ---------------- SETTINGS (2) ----------------
    {
        "id": "settings_001", "category": "settings", "quality_score": 41,
        "style": "crowded", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "single_column", "complexity": "high",
        "components": ["form", "toggle", "input"],
        "attributes": {"spacing": "cramped", "typography": "inconsistent", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 4, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["All settings sections shown on one long page with no grouping", "Toggle switches inconsistent in size across the page", "No clear save/confirmation pattern for changes"]
    },
    {
        "id": "settings_002", "category": "settings", "quality_score": 36,
        "style": "unclear_grouping", "industry": "saas", "framework": "unspecified",
        "theme": "dark", "layout": "tabs", "complexity": "medium",
        "components": ["form", "toggle", "input"],
        "attributes": {"spacing": "uneven", "typography": "mixed_fonts", "contrast": "low", "density": "moderate"},
        "design_tokens": {"padding": 8, "radius": 2, "shadow": "none", "spacing_unit": 4},
        "notes": ["Tab labels don't clearly indicate which is currently selected", "Related settings split across unrelated tabs", "Destructive actions styled the same as routine ones"]
    },
    # ---------------- MOBILE (2) ----------------
    {
        "id": "mobile_001", "category": "mobile", "quality_score": 32,
        "style": "tiny_touch_targets", "industry": "generic", "framework": "unspecified",
        "theme": "light", "layout": "single_column", "complexity": "medium",
        "components": ["card", "nav_item", "button"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 2, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Tap targets well under the 44px minimum recommended size", "Bottom nav icons crammed too close together for accurate taps", "Text requires zooming to read comfortably"]
    },
    {
        "id": "mobile_002", "category": "mobile", "quality_score": 35,
        "style": "desktop_squeezed", "industry": "crm", "framework": "unspecified",
        "theme": "light", "layout": "single_column", "complexity": "high",
        "components": ["table", "card"],
        "attributes": {"spacing": "cramped", "typography": "tiny", "contrast": "medium", "density": "overcrowded"},
        "design_tokens": {"padding": 2, "radius": 0, "shadow": "none", "spacing_unit": 2},
        "notes": ["Desktop table layout simply shrunk instead of redesigned for mobile", "Horizontal scrolling required to see all columns", "No mobile-specific navigation pattern, just a shrunk sidebar"]
    },
]

def main():
    count = 0
    for entry in ENTRIES:
        category = entry["category"]
        entry_id = entry["id"]
        out_dir = os.path.join(OUTPUT_ROOT, category)
        os.makedirs(out_dir, exist_ok=True)

        record = {
            "id": entry_id,
            "category": category,
            "quality": "poor",
            "quality_score": entry["quality_score"],
            "product": "AI-generated",
            "style": entry["style"],
            "industry": entry["industry"],
            "framework": entry["framework"],
            "theme": entry["theme"],
            "layout": entry["layout"],
            "complexity": entry["complexity"],
            "components": entry["components"],
            "attributes": entry["attributes"],
            "design_tokens": entry["design_tokens"],
            "notes": entry["notes"],
        }

        out_path = os.path.join(out_dir, f"{entry_id}.json")
        with open(out_path, "w") as f:
            json.dump(record, f, indent=2)
            f.write("\n")
        count += 1

    print(f"Generated {count} poor/ metadata files under {OUTPUT_ROOT}")

if __name__ == "__main__":
    main()
