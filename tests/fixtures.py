"""
Hand-written ParsedPage fixtures for rule engine tests.
No real parser involved — these are the ground-truth inputs.
"""
from __future__ import annotations


def clean_page() -> dict:
    """A near-perfect UI page — should trigger zero or minimal issues."""
    return {
        "fonts": ["Inter", "JetBrains Mono"],
        "headings": [
            {"level": 1, "font_size_px": 32.0, "text": "Dashboard"},
            {"level": 2, "font_size_px": 24.0, "text": "Overview"},
            {"level": 3, "font_size_px": 18.0, "text": "Details"},
        ],
        "body_font_size_px": 16.0,
        "line_height": 1.6,
        "buttons": [
            {
                "padding_top_px": 8.0,
                "padding_right_px": 16.0,
                "padding_bottom_px": 8.0,
                "padding_left_px": 16.0,
                "background_color": "#005fcc",
                "color": "#ffffff",
                "border_radius_px": 6.0,
                "has_focus_style": True,
                "height_px": 44.0,
                "text": "Save",
            },
            {
                "padding_top_px": 8.0,
                "padding_right_px": 16.0,
                "padding_bottom_px": 8.0,
                "padding_left_px": 16.0,
                "background_color": "#transparent",
                "color": "#005fcc",
                "border_radius_px": 6.0,
                "has_focus_style": True,
                "height_px": 44.0,
                "text": "Cancel",
            },
        ],
        "inputs": [
            {
                "has_label": True,
                "label_text": "Email",
                "placeholder": "you@example.com",
                "padding_px": 10.0,
                "has_focus_style": True,
                "input_type": "email",
            },
        ],
        "tables": [
            {
                "has_header": True,
                "has_zebra_striping": True,
                "cell_padding_px": 12.0,
                "has_border": True,
            },
        ],
        "cards": [
            {
                "padding_top_px": 24.0,
                "padding_right_px": 24.0,
                "padding_bottom_px": 24.0,
                "padding_left_px": 24.0,
            },
        ],
        "charts": [
            {
                "has_axis_labels": True,
                "color_count": 3,
                "colors": ["#005fcc", "#e65c00", "#2e7d32"],
            },
        ],
        "text_color_pairs": [
            {
                "foreground": "#111111",
                "background": "#ffffff",
                "font_size_px": 16.0,
                "is_bold": False,
                "context": "body",
            },
        ],
        "kpi_card_count": 4,
        "whitespace_ratio": 0.30,
        "spacing_values_px": [8.0, 16.0, 24.0, 32.0, 48.0],
    }


def bad_page() -> dict:
    """A poorly designed UI page — should trigger issues across all categories."""
    return {
        "fonts": ["Arial", "Helvetica", "Georgia", "Verdana"],  # too many
        "headings": [
            {"level": 1, "font_size_px": 20.0, "text": "Dashboard"},  # too small + weak hierarchy
            {"level": 2, "font_size_px": 18.0, "text": "Overview"},   # barely smaller than h1
        ],
        "body_font_size_px": 11.0,   # too small
        "line_height": 1.2,          # too tight
        "buttons": [
            {
                "padding_top_px": 3.0,
                "padding_right_px": 6.0,
                "padding_bottom_px": 3.0,
                "padding_left_px": 6.0,
                "background_color": "#ff0000",
                "color": "#ff6600",   # low contrast
                "border_radius_px": 2.0,
                "has_focus_style": False,
                "height_px": 28.0,
                "text": "Submit",
            },
            {
                "padding_top_px": 3.0,
                "padding_right_px": 6.0,
                "padding_bottom_px": 3.0,
                "padding_left_px": 6.0,
                "background_color": "#00aa00",
                "color": "#ffffff",
                "border_radius_px": 12.0,   # very different radius
                "has_focus_style": False,
                "height_px": 28.0,
                "text": "Cancel",
            },
            {
                "padding_top_px": 3.0,
                "padding_right_px": 6.0,
                "padding_bottom_px": 3.0,
                "padding_left_px": 6.0,
                "background_color": "#0000ff",
                "color": "#ffffff",
                "border_radius_px": 0.0,
                "has_focus_style": False,
                "height_px": 28.0,
                "text": "Delete",
            },
        ],
        "inputs": [
            {
                "has_label": False,
                "label_text": None,
                "placeholder": "Enter your email",  # placeholder as label
                "padding_px": 4.0,
                "has_focus_style": False,
                "input_type": "email",
            },
            {
                "has_label": False,
                "label_text": None,
                "placeholder": None,
                "padding_px": 4.0,
                "has_focus_style": False,
                "input_type": "text",
            },
        ],
        "tables": [
            {
                "has_header": False,
                "has_zebra_striping": False,
                "cell_padding_px": 3.0,
                "has_border": False,
            },
        ],
        "cards": [
            {
                "padding_top_px": 6.0,
                "padding_right_px": 6.0,
                "padding_bottom_px": 6.0,
                "padding_left_px": 6.0,
            },
        ],
        "charts": [
            {
                "has_axis_labels": False,
                "color_count": 3,
                "colors": ["#cccccc", "#dddddd", "#bbbbbb"],  # too similar
            },
        ],
        "text_color_pairs": [
            {
                "foreground": "#aaaaaa",   # light grey on white — low contrast
                "background": "#ffffff",
                "font_size_px": 14.0,
                "is_bold": False,
                "context": "body",
            },
        ],
        "kpi_card_count": 14,   # too many
        "whitespace_ratio": 0.08,  # very dense
        "spacing_values_px": [7.0, 13.0, 11.0, 22.0, 5.0, 19.0],  # off-grid
    }
