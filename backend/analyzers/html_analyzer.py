"""
HTML/CSS parser — converts raw HTML (plus optional external CSS) into a
ParsedPage dict that the scoring engine consumes directly.

Only handles what's needed to populate every ParsedPage field:
  fonts, headings, body_font_size_px, line_height,
  buttons, inputs, tables, cards, charts,
  text_color_pairs, kpi_card_count, whitespace_ratio, spacing_values_px.
"""
from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup, Tag

from backend.analyzers.css_parser import (
    get_padding,
    normalize_color,
    parse_css_rules,
    parse_font_families,
    parse_inline_style,
    parse_shorthand_padding,
    to_px,
)
from backend.models.analysis import ParsedPage

_CARD_KEYWORDS = frozenset({"card", "panel", "box", "tile", "widget", "paper"})
_KPI_KEYWORDS = frozenset({"kpi", "metric", "stat", "counter", "badge"})
_CHART_KEYWORDS = frozenset({"chart", "graph", "plot", "visualization"})
_HEADING_DEFAULTS = {1: 32.0, 2: 24.0, 3: 18.72, 4: 16.0, 5: 13.28, 6: 10.72}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(html: str, css: str = "") -> ParsedPage:
    """
    Parse raw HTML and optional external CSS into a ParsedPage dict.
    Inline <style> blocks are always included; pass linked-stylesheet
    text as `css` to include it too.
    """
    soup = BeautifulSoup(html, "html.parser")
    inline_css = "\n".join(tag.get_text() for tag in soup.find_all("style"))
    rules = parse_css_rules(inline_css + "\n" + css)

    return {
        "fonts": _fonts(soup, rules),
        "headings": _headings(soup, rules),
        "body_font_size_px": _body_font_size(soup, rules),
        "line_height": _line_height(soup, rules),
        "buttons": _buttons(soup, rules),
        "inputs": _inputs(soup, rules),
        "tables": _tables(soup, rules),
        "cards": _cards(soup, rules),
        "charts": _charts(soup, rules),
        "text_color_pairs": _text_color_pairs(soup, rules),
        "kpi_card_count": _kpi_count(soup),
        "whitespace_ratio": _whitespace_ratio(soup, rules),
        "spacing_values_px": _spacing_values(soup, rules),
    }


# ---------------------------------------------------------------------------
# Style resolution helpers
# ---------------------------------------------------------------------------

def _el_styles(el: Tag, rules: dict) -> dict[str, str]:
    """Merge CSS rules that match this element (tag → class → id → inline)."""
    styles: dict[str, str] = {}
    tag = el.name

    if tag in rules:
        styles.update(rules[tag])

    for cls in el.get("class", []):
        if f".{cls}" in rules:
            styles.update(rules[f".{cls}"])
        if f"{tag}.{cls}" in rules:
            styles.update(rules[f"{tag}.{cls}"])

    elem_id = el.get("id", "")
    if elem_id and f"#{elem_id}" in rules:
        styles.update(rules[f"#{elem_id}"])

    inline = el.get("style", "")
    if inline:
        styles.update(parse_inline_style(inline))

    return styles


def _has_focus_rule(el: Tag, rules: dict) -> bool:
    tag = el.name
    candidates = [f"{tag}:focus", f"{tag}:focus-visible", "*:focus", "*:focus-visible"]
    for cls in el.get("class", []):
        candidates += [
            f".{cls}:focus", f".{cls}:focus-visible",
            f"{tag}.{cls}:focus", f"{tag}.{cls}:focus-visible",
        ]
    return any(s in rules for s in candidates)


def _tag_styles(tag: str, rules: dict) -> dict[str, str]:
    return dict(rules.get(tag, {}))


# ---------------------------------------------------------------------------
# Field extractors
# ---------------------------------------------------------------------------

def _fonts(soup: BeautifulSoup, rules: dict) -> list[str]:
    seen: set[str] = set()
    for props in rules.values():
        for f in parse_font_families(props.get("font-family", "")):
            seen.add(f)
    for el in soup.find_all(style=True):
        for f in parse_font_families(parse_inline_style(el.get("style", "")).get("font-family", "")):
            seen.add(f)
    return sorted(seen)


def _body_font_size(soup: BeautifulSoup, rules: dict) -> Optional[float]:
    for sel in ("body", "html", ":root"):
        size = to_px(rules.get(sel, {}).get("font-size", ""))
        if size is not None:
            return size
    body = soup.find("body")
    if body and isinstance(body, Tag):
        size = to_px(parse_inline_style(body.get("style", "")).get("font-size", ""))
        if size is not None:
            return size
    return None


def _line_height(soup: BeautifulSoup, rules: dict) -> Optional[float]:
    for sel in ("body", "html", "*", "p"):
        lh = rules.get(sel, {}).get("line-height", "")
        if not lh:
            continue
        try:
            return float(lh)   # unitless ratio
        except ValueError:
            pass
        lh_px = to_px(lh)
        if lh_px:
            base = _body_font_size(soup, rules) or 16.0
            return round(lh_px / base, 2)
    return None


def _headings(soup: BeautifulSoup, rules: dict) -> list[dict]:
    result = []
    for level in range(1, 7):
        for el in soup.find_all(f"h{level}"):
            if not isinstance(el, Tag):
                continue
            styles = _el_styles(el, rules)
            size = to_px(styles.get("font-size", "")) or _HEADING_DEFAULTS[level]
            result.append({
                "level": level,
                "font_size_px": size,
                "text": el.get_text(strip=True)[:60],
            })
    return result


def _parse_button(el: Tag, rules: dict) -> dict:
    styles = _el_styles(el, rules)
    pt, pr, pb, pl = get_padding(styles)
    height = to_px(styles.get("height", "")) or to_px(styles.get("min-height", ""))
    if height is None:
        fs = to_px(styles.get("font-size", "16px")) or 16.0
        lh = to_px(styles.get("line-height", "")) or (fs * 1.5)
        height = pt + lh + pb
    return {
        "padding_top_px": pt,
        "padding_right_px": pr,
        "padding_bottom_px": pb,
        "padding_left_px": pl,
        "background_color": normalize_color(styles.get("background-color", "")) or "#cccccc",
        "color": normalize_color(styles.get("color", "")) or "#000000",
        "border_radius_px": to_px(styles.get("border-radius", "0")) or 0.0,
        "has_focus_style": _has_focus_rule(el, rules),
        "height_px": height,
        "text": el.get_text(strip=True) or el.get("value", ""),
    }


def _buttons(soup: BeautifulSoup, rules: dict) -> list[dict]:
    result = []
    for el in soup.find_all("button"):
        if isinstance(el, Tag):
            result.append(_parse_button(el, rules))
    for t in ("submit", "button", "reset"):
        for el in soup.find_all("input", attrs={"type": t}):
            if isinstance(el, Tag):
                result.append(_parse_button(el, rules))
    return result


def _inputs(soup: BeautifulSoup, rules: dict) -> list[dict]:
    skip = {"hidden", "submit", "button", "reset", "checkbox", "radio", "image"}
    label_map: dict[str, str] = {}
    for lbl in soup.find_all("label"):
        target = lbl.get("for", "")
        if target:
            label_map[target] = lbl.get_text(strip=True)

    result = []
    for el in soup.find_all(["input", "textarea", "select"]):
        if not isinstance(el, Tag):
            continue
        if el.name == "input" and el.get("type", "text").lower() in skip:
            continue

        styles = _el_styles(el, rules)
        pt, pr, pb, pl = get_padding(styles)
        pad = min(pt, pl) if (pt or pl) else (to_px(styles.get("padding", "0")) or 0.0)
        elem_id = el.get("id", "")
        has_label, label_text = False, None

        if elem_id and elem_id in label_map:
            has_label, label_text = True, label_map[elem_id]
        elif el.get("aria-label"):
            has_label, label_text = True, el.get("aria-label")
        else:
            parent = el.parent
            while parent and hasattr(parent, "name"):
                if parent.name == "label":
                    has_label = True
                    label_text = parent.get_text(strip=True)
                    break
                parent = getattr(parent, "parent", None)

        result.append({
            "has_label": has_label,
            "label_text": label_text,
            "placeholder": el.get("placeholder"),
            "padding_px": pad,
            "has_focus_style": _has_focus_rule(el, rules),
            "input_type": el.get("type", "text") if el.name == "input" else el.name,
        })
    return result


def _tables(soup: BeautifulSoup, rules: dict) -> list[dict]:
    result = []
    td_styles = _tag_styles("td", rules)
    th_styles = _tag_styles("th", rules)
    td_pad = get_padding(td_styles)
    th_pad = get_padding(th_styles)

    has_zebra = any(
        ("nth-child" in sel or "nth-of-type" in sel)
        and ("tr" in sel or "td" in sel or "row" in sel)
        for sel in rules
    )
    has_border = bool(
        td_styles.get("border") or td_styles.get("border-bottom")
        or th_styles.get("border") or rules.get("table", {}).get("border-collapse")
    )

    for table in soup.find_all("table"):
        if not isinstance(table, Tag):
            continue
        has_header = bool(table.find("thead") or table.find("th"))

        cell_pad = min(td_pad)
        if any(p > 0 for p in th_pad):
            cell_pad = min(cell_pad, min(th_pad))
        # Override from first <td> inline styles
        first_td = table.find("td")
        if first_td and isinstance(first_td, Tag):
            inline_pad = get_padding(_el_styles(first_td, rules))
            if any(p > 0 for p in inline_pad):
                cell_pad = min(cell_pad, min(inline_pad))

        result.append({
            "has_header": has_header,
            "has_zebra_striping": has_zebra,
            "cell_padding_px": cell_pad,
            "has_border": has_border,
        })
    return result


def _classes_contain(el: Tag, keywords: frozenset[str]) -> bool:
    classes = {c.lower() for c in el.get("class", [])}
    return any(kw in cls for cls in classes for kw in keywords)


def _cards(soup: BeautifulSoup, rules: dict) -> list[dict]:
    result = []
    for el in soup.find_all(True):
        if not isinstance(el, Tag) or not _classes_contain(el, _CARD_KEYWORDS):
            continue
        pt, pr, pb, pl = get_padding(_el_styles(el, rules))
        result.append({
            "padding_top_px": pt,
            "padding_right_px": pr,
            "padding_bottom_px": pb,
            "padding_left_px": pl,
        })
    return result


def _charts(soup: BeautifulSoup, rules: dict) -> list[dict]:
    result = []
    for el in soup.find_all(True):
        if not isinstance(el, Tag) or not _classes_contain(el, _CHART_KEYWORDS):
            continue
        colors: list[str] = []
        for child in el.find_all(True):
            st = parse_inline_style(child.get("style", ""))
            for prop in ("color", "background-color", "fill", "stroke"):
                c = normalize_color(st.get(prop, ""))
                if c and c not in colors:
                    colors.append(c)
        result.append({
            "has_axis_labels": bool(el.get("data-xlabel") or el.get("data-ylabel")),
            "color_count": len(colors),
            "colors": colors,
        })
    return result


def _text_color_pairs(soup: BeautifulSoup, rules: dict) -> list[dict]:
    body_s = rules.get("body", {})
    body_fg = normalize_color(body_s.get("color", "#333333")) or "#333333"
    body_bg = normalize_color(body_s.get("background-color", "#ffffff")) or "#ffffff"
    body_sz = to_px(body_s.get("font-size", "16px")) or 16.0

    pairs: list[dict] = []
    seen: set[tuple] = set()

    for tag in ("p", "span", "div", "td", "li", "a", "h1", "h2", "h3", "h4", "label"):
        for el in soup.find_all(tag):
            if not isinstance(el, Tag) or not el.get_text(strip=True):
                continue
            styles = _el_styles(el, rules)
            fg = normalize_color(styles.get("color", "")) or body_fg
            bg = normalize_color(styles.get("background-color", "")) or body_bg
            if not (fg and bg):
                continue
            sz = to_px(styles.get("font-size", "")) or body_sz
            bold = styles.get("font-weight", "") in ("bold", "700", "800", "900")
            ctx = tag if tag in ("a", "h1", "h2", "h3", "h4") else "body"
            key = (fg, bg, sz, bold)
            if key in seen:
                continue
            seen.add(key)
            pairs.append({
                "foreground": fg,
                "background": bg,
                "font_size_px": sz,
                "is_bold": bold,
                "context": ctx,
            })
            if len(pairs) >= 20:
                return pairs

    return pairs


def _kpi_count(soup: BeautifulSoup) -> int:
    count = 0
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        if _classes_contain(el, _KPI_KEYWORDS):
            count += 1
        elif any(kw in (el.get("id", "") or "").lower() for kw in _KPI_KEYWORDS):
            count += 1
    return count


def _whitespace_ratio(soup: BeautifulSoup, rules: dict) -> float:
    """Heuristic: average padding across block elements → mapped to 0.0–0.5."""
    total, count = 0.0, 0
    for el in soup.find_all(["div", "section", "article", "main", "aside", "header", "footer", "p"]):
        if not isinstance(el, Tag):
            continue
        avg = sum(get_padding(_el_styles(el, rules))) / 4
        if avg > 0:
            total += avg
            count += 1
    if count == 0:
        return 0.15
    return min(0.5, max(0.05, (total / count) / 80.0))


def _spacing_values(soup: BeautifulSoup, rules: dict) -> list[float]:
    """Collect every distinct non-zero padding/margin value found in CSS and inline styles."""
    values: set[float] = set()

    def _ingest(styles: dict[str, str]) -> None:
        for prop in ("padding", "margin", "gap", "row-gap", "column-gap"):
            raw = styles.get(prop, "")
            if raw:
                for v in parse_shorthand_padding(raw):
                    if v > 0:
                        values.add(v)
        for prop in (
            "padding-top", "padding-right", "padding-bottom", "padding-left",
            "margin-top", "margin-right", "margin-bottom", "margin-left",
        ):
            v = to_px(styles.get(prop, ""))
            if v and v > 0:
                values.add(v)

    for props in rules.values():
        _ingest(props)
    for el in soup.find_all(style=True):
        _ingest(parse_inline_style(el.get("style", "")))

    return sorted(values)
