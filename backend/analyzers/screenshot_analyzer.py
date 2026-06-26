"""
Screenshot analyzer — local CV-only layout and color analysis.
No API calls, no vision models. Runs entirely on OpenCV and Pillow.

Detectable from pixels : whitespace_ratio, text_color_pairs, spacing_values_px,
                         buttons (color + height), cards, tables, charts, kpi_card_count
Returned empty / None  : fonts, headings, body_font_size_px, line_height, inputs
                         (these require text recognition — use html_analyzer for HTML/CSS input)
"""
from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image

_MAX_DIM = 1200  # resize before processing so large screenshots stay fast


# ── public API ────────────────────────────────────────────────────────────────

def analyze(image_bytes: bytes) -> dict:
    """bytes → ParsedPage dict with CV-detectable fields populated."""
    pil_img = _load(image_bytes)
    arr = np.asarray(pil_img, dtype=np.uint8)
    rects = _find_rects(arr)
    return {
        "fonts": [],
        "headings": [],
        "body_font_size_px": None,
        "line_height": None,
        "buttons": _detect_buttons(rects, arr),
        "inputs": [],
        "tables": _detect_tables(arr),
        "cards": _detect_cards(rects, arr),
        "charts": _detect_charts(rects, arr),
        "text_color_pairs": _detect_text_color_pairs(pil_img),
        "kpi_card_count": _count_kpi_cards(rects),
        "whitespace_ratio": _whitespace_ratio(arr),
        "spacing_values_px": _spacing_values(rects),
    }


# ── image loading ─────────────────────────────────────────────────────────────

def _load(image_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size
    if max(w, h) > _MAX_DIM:
        scale = _MAX_DIM / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img


# ── pixel-level analysis ──────────────────────────────────────────────────────

def _whitespace_ratio(arr: np.ndarray) -> float:
    """Fraction of pixels with brightness ≥ 240 (near-white = empty space)."""
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    bright = int(np.sum(gray >= 240))
    ratio = bright / max(gray.size, 1)
    return round(min(max(ratio, 0.0), 1.0), 3)


def _detect_text_color_pairs(pil_img: Image.Image) -> list[dict]:
    """
    Sample a 200×200 downsample; separate dark (<80 brightness) from light (>210)
    pixels to infer the most likely text colour and background colour.
    """
    small = np.asarray(pil_img.resize((200, 200)), dtype=np.uint8)
    pixels = small.reshape(-1, 3).astype(np.float32)
    brightness = pixels.mean(axis=1)

    dark_px = pixels[brightness < 80].astype(np.uint8)
    light_px = pixels[brightness > 210].astype(np.uint8)

    if len(dark_px) < 10 or len(light_px) < 10:
        return []

    return [{
        "foreground": _most_common_hex(dark_px),
        "background": _most_common_hex(light_px),
        "font_size_px": 16.0,
        "is_bold": False,
        "context": "detected",
    }]


def _most_common_hex(pixels: np.ndarray) -> str:
    """Most frequent colour after 16-step quantisation."""
    q = (pixels.astype(np.uint16) // 16 * 16).astype(np.uint8)
    colors, counts = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    c = colors[int(np.argmax(counts))]
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


def _dominant_region_color(arr: np.ndarray, x: int, y: int, w: int, h: int) -> str:
    """Most common quantised colour inside a bounding box."""
    region = arr[y:y + h, x:x + w].reshape(-1, 3)
    q = (region.astype(np.uint16) // 16 * 16).astype(np.uint8)
    colors, counts = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    c = colors[int(np.argmax(counts))]
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


# ── contour / element detection ───────────────────────────────────────────────

def _find_rects(arr: np.ndarray) -> list[tuple[int, int, int, int]]:
    """
    Canny edge detection → dilation → contours → (x, y, w, h) bounding boxes.
    Uses RETR_LIST so elements nested inside cards are also returned.
    """
    h_img, w_img = arr.shape[:2]
    min_area = max(200, int(w_img * h_img * 0.001))

    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, 30, 100)
    dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    seen: set[tuple[int, ...]] = set()
    rects: list[tuple[int, int, int, int]] = []

    for c in contours:
        if cv2.contourArea(c) < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if w >= w_img * 0.95 and h >= h_img * 0.95:
            continue  # skip full-image frame noise
        key = (x // 8, y // 8, w // 8, h // 8)
        if key not in seen:
            seen.add(key)
            rects.append((x, y, w, h))

    return rects


# ── element classifiers ───────────────────────────────────────────────────────

# After 16-step quantisation, white and common light grays map here
_NEAR_WHITE = {
    "#f0f0f0", "#ffffff", "#f8f8f8", "#fafafa", "#efefef",
    "#f6f6f6", "#eeeeee", "#f4f4f4", "#e8e8e8", "#e0e0e0",
    "#d0d0d0", "#c8c8c8",
}


def _detect_buttons(rects: list[tuple], arr: np.ndarray) -> list[dict]:
    """
    Small rectangles that are wider than tall with a non-white fill.
    Padding and height are read from the bounding box; text/radius/focus
    cannot be recovered from pixels and are left at safe defaults.
    """
    h_img, w_img = arr.shape[:2]
    buttons = []
    for x, y, w, h in rects:
        if not (40 <= w <= min(400, w_img * 0.5) and 18 <= h <= 70 and w >= h * 1.2):
            continue
        inset_x, inset_y = min(2, w // 4), min(2, h // 4)
        bg = _dominant_region_color(
            arr, x + inset_x, y + inset_y,
            max(1, w - inset_x * 2), max(1, h - inset_y * 2),
        )
        if bg in _NEAR_WHITE:
            continue
        pad_y = round(max(4.0, h * 0.18), 1)
        pad_x = round(max(8.0, w * 0.14), 1)
        buttons.append({
            "padding_top_px": pad_y,
            "padding_right_px": pad_x,
            "padding_bottom_px": pad_y,
            "padding_left_px": pad_x,
            "background_color": bg,
            "color": "#ffffff",
            "border_radius_px": 0.0,
            "has_focus_style": False,
            "height_px": float(h),
            "text": "",
        })
    return buttons[:12]


def _detect_cards(rects: list[tuple], arr: np.ndarray) -> list[dict]:
    """Medium-to-large rectangular regions that aren't full-screen."""
    h_img, w_img = arr.shape[:2]
    cards = []
    for x, y, w, h in rects:
        area = w * h
        if not (100 <= w <= w_img * 0.92 and 60 <= h <= h_img * 0.92 and area >= 8000):
            continue
        pad = round(min(32.0, max(8.0, h * 0.08)), 1)
        cards.append({
            "padding_top_px": pad,
            "padding_right_px": pad,
            "padding_bottom_px": pad,
            "padding_left_px": pad,
        })
    return cards[:10]


def _detect_tables(arr: np.ndarray) -> list[dict]:
    """
    Morphological line extraction: significant horizontal AND vertical lines
    indicate a data table.
    """
    h_img, w_img = arr.shape[:2]
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2,
    )

    h_len = max(40, w_img // 10)
    v_len = max(30, h_img // 10)

    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_len, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_len))

    h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
    v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

    h_px = int(np.sum(h_lines > 0))
    v_px = int(np.sum(v_lines > 0))

    # Require at least 3 horizontal line-widths and some vertical coverage
    if h_px > w_img * 3 and v_px > h_img:
        return [{"has_header": True, "has_zebra_striping": False,
                 "cell_padding_px": 8.0, "has_border": True}]
    return []


def _detect_charts(rects: list[tuple], arr: np.ndarray) -> list[dict]:
    """
    Large regions containing multiple perceptually distinct mid-brightness
    colours (i.e. not just white background with dark text).
    """
    charts = []
    for x, y, w, h in rects:
        if w * h < 15000:
            continue
        region = arr[y:y + h, x:x + w]
        colors = _chart_colors(region)
        if len(colors) < 2:
            continue
        charts.append({
            "has_axis_labels": _has_axis_lines(region),
            "color_count": len(colors),
            "colors": colors,
        })
    return charts[:6]


def _chart_colors(region: np.ndarray) -> list[str]:
    """
    Dominant non-white, non-black colours in a region.
    Downsamples to 80×80 for speed; quantises to 40-step buckets.
    """
    small = cv2.resize(region, (80, 80), interpolation=cv2.INTER_AREA)
    pixels = small.reshape(-1, 3).astype(np.float32)
    brightness = pixels.mean(axis=1)
    mask = (brightness > 30) & (brightness < 215)
    filtered = pixels[mask].astype(np.uint8)
    if len(filtered) < 20:
        return []
    q = (filtered.astype(np.uint16) // 40 * 40).astype(np.uint8)
    colors, counts = np.unique(q.reshape(-1, 3), axis=0, return_counts=True)
    order = np.argsort(-counts)
    result = []
    for i in order:
        c = colors[i]
        result.append(f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}")
        if len(result) >= 6:
            break
    return result


def _has_axis_lines(region: np.ndarray) -> bool:
    """
    Heuristic: a consistently dark row in the bottom 15% of the region
    suggests a horizontal axis line.
    """
    h, w = region.shape[:2]
    if h < 30 or w < 30:
        return False
    gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
    bottom = gray[int(h * 0.80):int(h * 0.95), int(w * 0.05):int(w * 0.95)]
    if bottom.size == 0:
        return False
    return bool(bottom.min(axis=1).min() < 80)


# ── layout metrics ────────────────────────────────────────────────────────────

def _count_kpi_cards(rects: list[tuple]) -> int:
    """
    Count how many detected rectangles look like KPI cards:
    medium area and similar width to each other (within 35%).
    """
    candidates = [
        (w, h) for x, y, w, h in rects
        if 5000 <= w * h <= 80000 and 0.5 <= w / max(h, 1) <= 5.0
    ]
    if len(candidates) < 2:
        return 0
    widths = sorted(c[0] for c in candidates)
    median_w = widths[len(widths) // 2]
    similar = sum(1 for cw in widths if abs(cw - median_w) / max(median_w, 1) < 0.35)
    return similar if similar >= 2 else 0


def _spacing_values(rects: list[tuple]) -> list[float]:
    """
    Vertical and horizontal gaps between adjacent detected elements,
    rounded to the nearest 4 px and deduplicated.
    """
    if len(rects) < 2:
        return []
    sorted_r = sorted(rects, key=lambda r: (r[1], r[0]))
    gaps: set[float] = set()
    for i in range(len(sorted_r) - 1):
        x1, y1, w1, h1 = sorted_r[i]
        x2, y2, w2, h2 = sorted_r[i + 1]
        v_gap = y2 - (y1 + h1)
        if 2 < v_gap < 160:
            gaps.add(float(round(v_gap / 4) * 4))
        if abs(y2 - y1) < max(h1, h2) * 0.6:
            h_gap = x2 - (x1 + w1)
            if 2 < h_gap < 160:
                gaps.add(float(round(h_gap / 4) * 4))
    return sorted(gaps)
