"""
Deterministic unit tests for the screenshot analyzer.

Every test image is synthesised with Pillow — known pixel geometry, no file I/O,
no randomness, no network.  Tests assert on measurable pixel outcomes
(whitespace ratio, dominant colors, element counts) rather than exact coordinates,
because edge detection can shift bounding boxes by a pixel or two.
"""
from __future__ import annotations

import io

import pytest
from PIL import Image, ImageDraw

from backend.analyzers import screenshot_analyzer


# ── image factories ───────────────────────────────────────────────────────────

def _png(pil_img: Image.Image) -> bytes:
    buf = io.BytesIO()
    pil_img.save(buf, "PNG")
    return buf.getvalue()


def _blank_white(w: int = 600, h: int = 400) -> bytes:
    return _png(Image.new("RGB", (w, h), (255, 255, 255)))


def _all_dark(w: int = 600, h: int = 400) -> bytes:
    return _png(Image.new("RGB", (w, h), (40, 40, 40)))


def _with_button(
    btn_x: int = 230, btn_y: int = 178,
    btn_w: int = 140, btn_h: int = 44,
    color: tuple = (0, 102, 204),
) -> bytes:
    """White canvas with one clearly button-sized coloured rectangle."""
    img = Image.new("RGB", (600, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([btn_x, btn_y, btn_x + btn_w, btn_y + btn_h], fill=color)
    return _png(img)


def _with_card() -> bytes:
    """White canvas with one large bordered rectangle (card)."""
    img = Image.new("RGB", (600, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 560, 360], outline=(0, 0, 0), width=2, fill=(248, 248, 248))
    return _png(img)


def _with_table() -> bytes:
    """White canvas with a 5×4 grid (table lines)."""
    img = Image.new("RGB", (600, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for y in range(100, 320, 44):           # 5 horizontal lines, each 440 px wide
        draw.line([(80, y), (520, y)], fill=(0, 0, 0), width=1)
    for x in range(80, 521, 110):           # 5 vertical lines, each 220 px tall
        draw.line([(x, 100), (x, 320)], fill=(0, 0, 0), width=1)
    return _png(img)


def _with_chart() -> bytes:
    """White canvas with a bordered region filled by 4 distinct-colour bars."""
    img = Image.new("RGB", (600, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 560, 360], outline=(0, 0, 0), fill=(240, 240, 240))
    # 4 bars — clearly distinct perceptual colours
    bars = [
        ((70,  80, 540, 360), (0,   102, 204)),   # blue
        ((170, 120, 540, 360), (210, 70,  10)),    # orange
        ((270, 60,  540, 360), (30,  130, 50)),    # green
        ((370, 100, 540, 360), (140, 30,  160)),   # purple
    ]
    for (x0, y0, x1, y1), color in bars:
        draw.rectangle([x0, y0, x1, y1], fill=color)
    return _png(img)


def _dark_on_white() -> bytes:
    """White canvas with dark-blue 'text' blocks — used for color-pair detection."""
    img = Image.new("RGB", (600, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50,  60, 420,  90], fill=(15, 15, 55))
    draw.rectangle([50, 110, 360, 130], fill=(20, 20, 40))
    draw.rectangle([50, 140, 300, 160], fill=(20, 20, 40))
    return _png(img)


def _four_kpi_cards() -> bytes:
    """Four similar-sized bordered rectangles in a row — KPI cards."""
    img = Image.new("RGB", (800, 220), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(4):
        x = 20 + i * 190
        draw.rectangle([x, 20, x + 170, 200], outline=(0, 0, 0), width=2,
                       fill=(250, 250, 250))
    return _png(img)


def _spaced_elements() -> bytes:
    """Coloured blocks with a consistent 20 px vertical gap."""
    img = Image.new("RGB", (400, 500), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(4):
        y = 40 + i * 100          # height 80 px, gap 20 px
        draw.rectangle([100, y, 300, y + 80], fill=(0, 100, 200))
    return _png(img)


def _mostly_white_small_element() -> bytes:
    img = Image.new("RGB", (600, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([280, 185, 320, 215], fill=(200, 50, 50))   # small red square
    return _png(img)


# ── helper ────────────────────────────────────────────────────────────────────

def _hex_brightness(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r + g + b) / 3


# ── tests: whitespace ratio ───────────────────────────────────────────────────

class TestWhitespaceRatio:
    def test_all_white_image_approaches_one(self):
        r = screenshot_analyzer.analyze(_blank_white())
        assert r["whitespace_ratio"] >= 0.95

    def test_all_dark_image_approaches_zero(self):
        r = screenshot_analyzer.analyze(_all_dark())
        assert r["whitespace_ratio"] < 0.05

    def test_ratio_is_between_zero_and_one(self):
        for img_bytes in [_blank_white(), _all_dark(), _with_button()]:
            ratio = screenshot_analyzer.analyze(img_bytes)["whitespace_ratio"]
            assert 0.0 <= ratio <= 1.0

    def test_mostly_white_with_small_element_still_high(self):
        r = screenshot_analyzer.analyze(_mostly_white_small_element())
        assert r["whitespace_ratio"] > 0.80

    def test_chart_image_has_lower_whitespace_than_blank(self):
        blank_ratio = screenshot_analyzer.analyze(_blank_white())["whitespace_ratio"]
        chart_ratio = screenshot_analyzer.analyze(_with_chart())["whitespace_ratio"]
        assert chart_ratio < blank_ratio


# ── tests: text colour pairs ──────────────────────────────────────────────────

class TestTextColorPairs:
    def test_blank_white_has_no_pairs(self):
        r = screenshot_analyzer.analyze(_blank_white())
        assert r["text_color_pairs"] == []

    def test_all_dark_has_no_pairs(self):
        # No light pixels above 210
        r = screenshot_analyzer.analyze(_all_dark())
        assert r["text_color_pairs"] == []

    def test_dark_on_white_returns_one_pair(self):
        r = screenshot_analyzer.analyze(_dark_on_white())
        assert len(r["text_color_pairs"]) == 1

    def test_foreground_is_dark(self):
        r = screenshot_analyzer.analyze(_dark_on_white())
        fg = r["text_color_pairs"][0]["foreground"]
        assert _hex_brightness(fg) < 100, f"Expected dark fg, got {fg}"

    def test_background_is_light(self):
        r = screenshot_analyzer.analyze(_dark_on_white())
        bg = r["text_color_pairs"][0]["background"]
        assert _hex_brightness(bg) > 180, f"Expected light bg, got {bg}"

    def test_pair_has_required_fields(self):
        r = screenshot_analyzer.analyze(_dark_on_white())
        pair = r["text_color_pairs"][0]
        assert "foreground" in pair
        assert "background" in pair
        assert pair["font_size_px"] == 16.0
        assert pair["is_bold"] is False
        assert pair["context"] == "detected"


# ── tests: button detection ───────────────────────────────────────────────────

class TestButtonDetection:
    def test_blank_image_has_no_buttons(self):
        assert screenshot_analyzer.analyze(_blank_white())["buttons"] == []

    def test_coloured_button_rect_detected(self):
        r = screenshot_analyzer.analyze(_with_button())
        assert len(r["buttons"]) >= 1

    def test_button_background_is_not_white(self):
        r = screenshot_analyzer.analyze(_with_button())
        for btn in r["buttons"]:
            assert btn["background_color"] not in screenshot_analyzer._NEAR_WHITE

    def test_button_height_matches_drawn_height(self):
        r = screenshot_analyzer.analyze(_with_button(btn_h=44))
        heights = [b["height_px"] for b in r["buttons"]]
        assert any(40 <= h <= 50 for h in heights), f"Heights: {heights}"

    def test_button_has_padding_fields(self):
        r = screenshot_analyzer.analyze(_with_button())
        btn = r["buttons"][0]
        for field in ("padding_top_px", "padding_right_px",
                      "padding_bottom_px", "padding_left_px"):
            assert field in btn
            assert btn[field] > 0

    def test_white_fill_rect_not_detected_as_button(self):
        img = Image.new("RGB", (600, 400), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([200, 180, 400, 220], fill=(255, 255, 255))
        r = screenshot_analyzer.analyze(_png(img))
        assert r["buttons"] == []

    def test_too_tall_rect_not_a_button(self):
        """A square element (w == h) must not be classified as a button."""
        img = Image.new("RGB", (600, 400), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([200, 150, 400, 250], fill=(0, 100, 200))  # 200×100 — w/h=2 but h=100>70
        r = screenshot_analyzer.analyze(_png(img))
        assert all(b["height_px"] <= 70 for b in r["buttons"])


# ── tests: card detection ─────────────────────────────────────────────────────

class TestCardDetection:
    def test_blank_image_has_no_cards(self):
        assert screenshot_analyzer.analyze(_blank_white())["cards"] == []

    def test_large_bordered_rect_detected_as_card(self):
        r = screenshot_analyzer.analyze(_with_card())
        assert len(r["cards"]) >= 1

    def test_card_has_positive_padding(self):
        r = screenshot_analyzer.analyze(_with_card())
        for card in r["cards"]:
            assert card["padding_top_px"] > 0
            assert card["padding_left_px"] > 0

    def test_card_has_all_padding_fields(self):
        r = screenshot_analyzer.analyze(_with_card())
        card = r["cards"][0]
        for field in ("padding_top_px", "padding_right_px",
                      "padding_bottom_px", "padding_left_px"):
            assert field in card


# ── tests: table detection ────────────────────────────────────────────────────

class TestTableDetection:
    def test_blank_image_has_no_tables(self):
        assert screenshot_analyzer.analyze(_blank_white())["tables"] == []

    def test_grid_lines_detected_as_table(self):
        r = screenshot_analyzer.analyze(_with_table())
        assert len(r["tables"]) >= 1

    def test_table_has_required_fields(self):
        r = screenshot_analyzer.analyze(_with_table())
        table = r["tables"][0]
        for field in ("has_header", "has_zebra_striping", "cell_padding_px", "has_border"):
            assert field in table

    def test_table_cell_padding_is_positive(self):
        r = screenshot_analyzer.analyze(_with_table())
        assert r["tables"][0]["cell_padding_px"] > 0


# ── tests: chart detection ────────────────────────────────────────────────────

class TestChartDetection:
    def test_blank_image_has_no_charts(self):
        assert screenshot_analyzer.analyze(_blank_white())["charts"] == []

    def test_multicolor_region_detected_as_chart(self):
        r = screenshot_analyzer.analyze(_with_chart())
        assert len(r["charts"]) >= 1

    def test_chart_has_at_least_two_colors(self):
        r = screenshot_analyzer.analyze(_with_chart())
        for chart in r["charts"]:
            assert len(chart["colors"]) >= 2

    def test_chart_color_count_matches_colors_list(self):
        r = screenshot_analyzer.analyze(_with_chart())
        for chart in r["charts"]:
            assert chart["color_count"] == len(chart["colors"])

    def test_chart_has_axis_label_field(self):
        r = screenshot_analyzer.analyze(_with_chart())
        for chart in r["charts"]:
            assert isinstance(chart["has_axis_labels"], bool)


# ── tests: KPI card count ─────────────────────────────────────────────────────

class TestKpiCardCount:
    def test_blank_image_has_zero_kpi_cards(self):
        assert screenshot_analyzer.analyze(_blank_white())["kpi_card_count"] == 0

    def test_four_similar_cards_counted(self):
        r = screenshot_analyzer.analyze(_four_kpi_cards())
        assert r["kpi_card_count"] >= 3

    def test_kpi_count_is_non_negative(self):
        for img_bytes in [_blank_white(), _with_button(), _four_kpi_cards()]:
            assert screenshot_analyzer.analyze(img_bytes)["kpi_card_count"] >= 0


# ── tests: spacing values ─────────────────────────────────────────────────────

class TestSpacingValues:
    def test_blank_image_has_no_spacing(self):
        assert screenshot_analyzer.analyze(_blank_white())["spacing_values_px"] == []

    def test_spaced_elements_yield_spacing_values(self):
        r = screenshot_analyzer.analyze(_spaced_elements())
        assert len(r["spacing_values_px"]) >= 1

    def test_spacing_values_are_positive(self):
        r = screenshot_analyzer.analyze(_spaced_elements())
        for v in r["spacing_values_px"]:
            assert v > 0

    def test_spacing_values_are_sorted(self):
        r = screenshot_analyzer.analyze(_spaced_elements())
        vals = r["spacing_values_px"]
        assert vals == sorted(vals)


# ── tests: ParsedPage structure ───────────────────────────────────────────────

class TestParsedPageStructure:
    _REQUIRED_KEYS = {
        "fonts", "headings", "body_font_size_px", "line_height",
        "buttons", "inputs", "tables", "cards", "charts",
        "text_color_pairs", "kpi_card_count", "whitespace_ratio", "spacing_values_px",
    }

    def test_all_required_keys_present(self):
        r = screenshot_analyzer.analyze(_blank_white())
        assert self._REQUIRED_KEYS == set(r.keys())

    def test_non_cv_fields_are_empty_or_none(self):
        r = screenshot_analyzer.analyze(_blank_white())
        assert r["fonts"] == []
        assert r["headings"] == []
        assert r["body_font_size_px"] is None
        assert r["line_height"] is None
        assert r["inputs"] == []

    def test_whitespace_ratio_is_float(self):
        r = screenshot_analyzer.analyze(_blank_white())
        assert isinstance(r["whitespace_ratio"], float)

    def test_kpi_card_count_is_int(self):
        r = screenshot_analyzer.analyze(_blank_white())
        assert isinstance(r["kpi_card_count"], int)

    def test_scoring_engine_accepts_output(self):
        from backend.services import scoring_engine
        result = scoring_engine.analyze(screenshot_analyzer.analyze(_with_chart()))
        assert 0 <= result.overall_score <= 100


# ── tests: image format and size variants ────────────────────────────────────

class TestImageVariants:
    def test_jpeg_input_accepted(self):
        img = Image.new("RGB", (400, 300), (255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=95)
        r = screenshot_analyzer.analyze(buf.getvalue())
        assert "whitespace_ratio" in r

    def test_large_image_downscaled_and_processed(self):
        img = Image.new("RGB", (2400, 1600), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([500, 400, 900, 800], fill=(0, 100, 200))
        r = screenshot_analyzer.analyze(_png(img))
        assert "whitespace_ratio" in r
        assert r["whitespace_ratio"] > 0.8

    def test_portrait_orientation(self):
        img = Image.new("RGB", (300, 700), (255, 255, 255))
        r = screenshot_analyzer.analyze(_png(img))
        assert 0.0 <= r["whitespace_ratio"] <= 1.0

    def test_wide_landscape_orientation(self):
        img = Image.new("RGB", (1200, 300), (255, 255, 255))
        r = screenshot_analyzer.analyze(_png(img))
        assert 0.0 <= r["whitespace_ratio"] <= 1.0
