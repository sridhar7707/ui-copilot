"""
Generates the 'excellent' benchmark metadata JSON files for UICopilot's
Module 3b Benchmark Library (Pack 1).

These pair with the renamed PNGs produced by rename_benchmark_images.sh:
data/benchmarks/images/excellent/{category}/{id}.png

Covers 30 of the 32 target excellent images. Two are intentionally absent
(tables_004, metrics_002) because the source image set was missing
excellent_table_04.png and excellent_metrics_02.png — generate those two
images separately, then add matching JSON entries using this file as a
template.

Run: python scripts/generate_excellent_metadata.py
Output: data/benchmarks/images/excellent/{category}/{id}.json
"""

import json
import os

OUTPUT_ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "benchmarks", "images", "excellent")

ENTRIES = [
    # ---------------- DASHBOARDS (8) ----------------
    {
        "id": "dashboard_001", "category": "dashboards", "quality_score": 91,
        "style": "minimal", "industry": "analytics", "theme": "light",
        "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "line_chart", "kpi_metric"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 8, "shadow": "light", "spacing_unit": 8},
        "notes": ["Calm, single-color accent against a neutral palette", "Generous whitespace around the primary chart", "Sidebar nav clearly separated from content"]
    },
    {
        "id": "dashboard_002", "category": "dashboards", "quality_score": 89,
        "style": "minimal", "industry": "saas", "theme": "dark",
        "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "line_chart", "kpi_metric"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "none", "spacing_unit": 8},
        "notes": ["Dark theme with sufficient contrast on key numbers", "Single donut chart given clear visual priority", "Consistent icon weight throughout sidebar"]
    },
    {
        "id": "dashboard_003", "category": "dashboards", "quality_score": 93,
        "style": "modern", "industry": "analytics", "theme": "light",
        "layout": "topnav", "complexity": "medium",
        "components": ["topbar", "bar_chart", "donut_chart", "kpi_metric"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "excellent", "density": "comfortable"},
        "design_tokens": {"padding": 24, "radius": 12, "shadow": "light", "spacing_unit": 8},
        "notes": ["Clear hierarchy between primary chart and supporting donut", "Bar chart uses a restrained two-color palette", "Section labels in consistent small-caps style"]
    },
    {
        "id": "dashboard_004", "category": "dashboards", "quality_score": 90,
        "style": "bold_minimal", "industry": "finance", "theme": "light",
        "layout": "topnav", "complexity": "low",
        "components": ["bar_chart", "kpi_metric"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Purple accent used consistently for the single chart", "Single focal metric at top with no competing numbers", "Plenty of negative space framing the chart"]
    },
    {
        "id": "dashboard_005", "category": "dashboards", "quality_score": 88,
        "style": "minimal", "industry": "crm", "theme": "light",
        "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "donut_chart", "kpi_metric"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "light", "spacing_unit": 8},
        "notes": ["Donut chart and metric numbers given equal balanced weight", "Sidebar icons all from a single consistent set", "Comfortable line-height on all label text"]
    },
    {
        "id": "dashboard_006", "category": "dashboards", "quality_score": 92,
        "style": "modern", "industry": "saas", "theme": "light",
        "layout": "sidebar", "complexity": "low",
        "components": ["sidebar", "line_chart"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "excellent", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 8, "shadow": "light", "spacing_unit": 8},
        "notes": ["Single smooth area chart as the clear focal point", "Soft gradient fill used tastefully, not distractingly", "Sidebar kept visually quiet to not compete with the chart"]
    },
    {
        "id": "dashboard_007", "category": "dashboards", "quality_score": 87,
        "style": "minimal", "industry": "finance", "theme": "dark",
        "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "bar_chart", "kpi_metric", "donut_chart"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "none", "spacing_unit": 8},
        "notes": ["Dark theme maintains good contrast on bars and labels", "Bar and donut charts share a consistent color system", "Sidebar nav items have generous vertical spacing"]
    },
    {
        "id": "dashboard_008", "category": "dashboards", "quality_score": 90,
        "style": "modern", "industry": "analytics", "theme": "light",
        "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "line_chart", "donut_chart", "kpi_metric"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "light", "spacing_unit": 8},
        "notes": ["Clean grid alignment between chart panels", "Consistent green accent used for positive trend indicators", "Clear visual separation between sidebar and main content"]
    },
    # ---------------- CARDS (4) ----------------
    {
        "id": "cards_001", "category": "cards", "quality_score": 88,
        "style": "minimal", "industry": "crm", "theme": "light",
        "layout": "grid", "complexity": "low",
        "components": ["card", "avatar"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 12, "shadow": "light", "spacing_unit": 8},
        "notes": ["Consistent avatar size and placement across cards", "Equal padding on all sides of each card", "Subtle shadow gives gentle depth without distraction"]
    },
    {
        "id": "cards_002", "category": "cards", "quality_score": 86,
        "style": "minimal", "industry": "saas", "theme": "light",
        "layout": "grid", "complexity": "low",
        "components": ["card", "avatar", "badge"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "light", "spacing_unit": 8},
        "notes": ["Status badges use a single consistent color system", "Card titles and metadata clearly differentiated by weight", "Comfortable spacing between stacked cards"]
    },
    {
        "id": "cards_003", "category": "cards", "quality_score": 90,
        "style": "modern", "industry": "finance", "theme": "light",
        "layout": "grid", "complexity": "low",
        "components": ["card", "kpi_metric"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "excellent", "density": "comfortable"},
        "design_tokens": {"padding": 24, "radius": 14, "shadow": "light", "spacing_unit": 8},
        "notes": ["Large KPI number given clear visual priority over label", "Trend indicator color and direction are unambiguous", "Generous internal padding keeps the card feeling uncluttered"]
    },
    {
        "id": "cards_004", "category": "cards", "quality_score": 89,
        "style": "minimal", "industry": "analytics", "theme": "light",
        "layout": "grid", "complexity": "low",
        "components": ["card", "sparkline"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "light", "spacing_unit": 8},
        "notes": ["Sparkline sits cleanly below the metric with clear separation", "Single accent color used consistently for the trend line", "Card corners and shadow match the rest of the design system"]
    },
    # ---------------- TABLES (3 — one image missing) ----------------
    {
        "id": "tables_001", "category": "tables", "quality_score": 87,
        "style": "minimal", "industry": "generic", "theme": "light",
        "layout": "full_width", "complexity": "medium",
        "components": ["table", "badge"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 16, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Generous row height makes scanning easy", "Header row clearly distinguished by weight and color", "Status badges use a consistent, limited color palette"]
    },
    {
        "id": "tables_002", "category": "tables", "quality_score": 85,
        "style": "minimal", "industry": "crm", "theme": "light",
        "layout": "full_width", "complexity": "medium",
        "components": ["table", "avatar", "badge"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 16, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Consistent column alignment across all rows", "Subtle row separators without heavy borders", "Avatar and name pairing kept visually tidy"]
    },
    {
        "id": "tables_003", "category": "tables", "quality_score": 88,
        "style": "modern", "industry": "saas", "theme": "light",
        "layout": "full_width", "complexity": "medium",
        "components": ["table", "badge"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "excellent", "density": "comfortable"},
        "design_tokens": {"padding": 16, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Clear visual hierarchy between header and data rows", "Numeric columns right-aligned for easy scanning", "Sort indicators on headers are unambiguous"]
    },
    # tables_004 intentionally omitted — source PNG not yet generated
    # ---------------- FORMS (4) ----------------
    {
        "id": "forms_001", "category": "forms", "quality_score": 88,
        "style": "minimal", "industry": "saas_login", "theme": "dark",
        "layout": "single_column", "complexity": "low",
        "components": ["form", "input", "button"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Single primary CTA clearly distinguished from secondary links", "Comfortable spacing between label and input", "Dark theme maintains good contrast on input borders"]
    },
    {
        "id": "forms_002", "category": "forms", "quality_score": 87,
        "style": "minimal", "industry": "saas_signup", "theme": "light",
        "layout": "single_column", "complexity": "low",
        "components": ["form", "input", "button"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Clear visual focus state implied by consistent input style", "Generous vertical rhythm between form fields", "Primary button full-width and unmistakably the next step"]
    },
    {
        "id": "forms_003", "category": "forms", "quality_score": 86,
        "style": "minimal", "industry": "fintech", "theme": "light",
        "layout": "single_column", "complexity": "medium",
        "components": ["form", "input", "button", "validation_icon"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Validation state shown clearly with both icon and color", "Field grouping (card number, expiry, CVC) logically arranged", "Consistent input height across the whole form"]
    },
    {
        "id": "forms_004", "category": "forms", "quality_score": 89,
        "style": "minimal", "industry": "saas", "theme": "light",
        "layout": "single_column", "complexity": "low",
        "components": ["form", "input", "button"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Short, focused form with no unnecessary fields", "Clear single call-to-action with no competing buttons", "Comfortable whitespace around the entire form card"]
    },
    # ---------------- NAVIGATION (4) ----------------
    {
        "id": "navigation_001", "category": "navigation", "quality_score": 90,
        "style": "minimal", "industry": "saas", "theme": "dark",
        "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "nav_item"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 16, "radius": 8, "shadow": "none", "spacing_unit": 8},
        "notes": ["Active nav item clearly highlighted with consistent treatment", "Icon and label alignment consistent down the whole list", "Comfortable spacing between nav groups"]
    },
    {
        "id": "navigation_002", "category": "navigation", "quality_score": 88,
        "style": "minimal", "industry": "project_management", "theme": "dark",
        "layout": "sidebar", "complexity": "medium",
        "components": ["sidebar", "nav_item"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 16, "radius": 6, "shadow": "none", "spacing_unit": 8},
        "notes": ["Clean grouping between workspace switcher and nav items", "Single consistent icon weight throughout", "Subtle hover/active distinction without visual noise"]
    },
    {
        "id": "navigation_003", "category": "navigation", "quality_score": 87,
        "style": "minimal", "industry": "generic", "theme": "light",
        "layout": "sidebar", "complexity": "low",
        "components": ["sidebar", "nav_item"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 16, "radius": 6, "shadow": "none", "spacing_unit": 8},
        "notes": ["Minimal icon set with generous spacing between items", "Clear section divider between primary and secondary nav", "Comfortable touch/click target size on each item"]
    },
    {
        "id": "navigation_004", "category": "navigation", "quality_score": 89,
        "style": "minimal", "industry": "saas", "theme": "dark",
        "layout": "topnav", "complexity": "low",
        "components": ["topbar", "nav_item"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 16, "radius": 6, "shadow": "none", "spacing_unit": 8},
        "notes": ["Top nav items evenly spaced with clear active state", "Workspace name and breadcrumb kept visually subordinate", "Consistent button style for the single primary action"]
    },
    # ---------------- CHARTS (4) ----------------
    {
        "id": "charts_001", "category": "charts", "quality_score": 88,
        "style": "minimal", "industry": "analytics", "theme": "light",
        "layout": "card", "complexity": "low",
        "components": ["line_chart"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "light", "spacing_unit": 8},
        "notes": ["Two clearly distinguishable line series with a legend", "Axis labels legible without crowding the plot area", "Restrained color palette appropriate for the data"]
    },
    {
        "id": "charts_002", "category": "charts", "quality_score": 87,
        "style": "minimal", "industry": "analytics", "theme": "light",
        "layout": "card", "complexity": "low",
        "components": ["bar_chart"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "light", "spacing_unit": 8},
        "notes": ["Bars evenly spaced with clear category labels", "Single consistent color used across all bars", "Gridlines subtle enough to not compete with the data"]
    },
    {
        "id": "charts_003", "category": "charts", "quality_score": 90,
        "style": "modern", "industry": "saas", "theme": "light",
        "layout": "card", "complexity": "low",
        "components": ["donut_chart"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "excellent", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 12, "shadow": "light", "spacing_unit": 8},
        "notes": ["Clear legend with distinct, harmonious slice colors", "Center label gives the chart a clear focal point", "Generous surrounding whitespace"]
    },
    {
        "id": "charts_004", "category": "charts", "quality_score": 86,
        "style": "minimal", "industry": "finance", "theme": "light",
        "layout": "card", "complexity": "low",
        "components": ["bar_chart"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "comfortable"},
        "design_tokens": {"padding": 20, "radius": 10, "shadow": "light", "spacing_unit": 8},
        "notes": ["Single blue accent used consistently across all bars", "Clear axis title and units", "Comfortable spacing between bars avoids a cluttered look"]
    },
    # ---------------- METRICS (3 — one image missing) ----------------
    {
        "id": "metrics_001", "category": "metrics", "quality_score": 91,
        "style": "minimal", "industry": "saas", "theme": "light",
        "layout": "card", "complexity": "low",
        "components": ["kpi_metric", "sparkline"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 12, "shadow": "light", "spacing_unit": 8},
        "notes": ["Large, bold metric value with clear visual priority", "Trend percentage color-coded and unambiguous", "Comparison period clearly labeled for context"]
    },
    # metrics_002 intentionally omitted — source PNG not yet generated
    {
        "id": "metrics_003", "category": "metrics", "quality_score": 89,
        "style": "minimal", "industry": "saas", "theme": "light",
        "layout": "card", "complexity": "low",
        "components": ["kpi_metric", "sparkline"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "good", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 12, "shadow": "light", "spacing_unit": 8},
        "notes": ["Clean alignment between label, value, and trend indicator", "Sparkline color matches the trend direction", "Generous padding keeps the card feeling calm"]
    },
    {
        "id": "metrics_004", "category": "metrics", "quality_score": 90,
        "style": "minimal", "industry": "saas", "theme": "light",
        "layout": "card", "complexity": "low",
        "components": ["kpi_metric", "sparkline"],
        "attributes": {"spacing": "excellent", "typography": "clear", "contrast": "excellent", "density": "spacious"},
        "design_tokens": {"padding": 24, "radius": 12, "shadow": "light", "spacing_unit": 8},
        "notes": ["Percentage metric formatted clearly with appropriate precision", "Consistent card styling matching the rest of the metrics row", "Trend arrow direction and color are unambiguous"]
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
            "quality": "excellent",
            "quality_score": entry["quality_score"],
            "product": "AI-generated",
            "style": entry["style"],
            "industry": entry["industry"],
            "framework": "unspecified",
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

    print(f"Generated {count} excellent/ metadata files under {OUTPUT_ROOT}")
    print("Missing: tables_004, metrics_002 (source PNGs not yet generated)")

if __name__ == "__main__":
    main()
