"""
CSS text utilities shared by the HTML analyzer.
Parses raw CSS into a selector→properties map and normalises values to pixels/hex.
"""
from __future__ import annotations

import re
from typing import Optional

_BASE_FONT_PX = 16.0  # browser default

_NAMED_COLORS: dict[str, str] = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000",
    "green": "#008000", "blue": "#0000ff", "gray": "#808080",
    "grey": "#808080", "silver": "#c0c0c0", "yellow": "#ffff00",
    "orange": "#ffa500", "purple": "#800080", "pink": "#ffc0cb",
    "brown": "#a52a2a", "navy": "#000080", "teal": "#008080",
    "transparent": "#ffffff",
}

_GENERIC_FONT_KEYWORDS = frozenset({
    "serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
    "ui-serif", "ui-sans-serif", "ui-monospace",
})


def parse_css_rules(css_text: str) -> dict[str, dict[str, str]]:
    """
    Parse CSS text into {selector: {property: value}}.
    Handles comma-separated selectors. Skips @-rules.
    """
    # Strip comments
    css_text = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    # Strip @-rules (simplified — no nested support needed for our HTML samples)
    css_text = re.sub(r"@[^{]+\{[^{}]*\}", "", css_text, flags=re.DOTALL)

    rules: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"([^{@]+)\{([^}]*)\}", css_text):
        raw_selectors = match.group(1).strip()
        declarations = match.group(2).strip()

        props: dict[str, str] = {}
        for decl in declarations.split(";"):
            decl = decl.strip()
            if ":" not in decl:
                continue
            prop, _, value = decl.partition(":")
            prop = prop.strip().lower()
            value = value.strip()
            if prop and value:
                props[prop] = value

        if not props:
            continue

        for selector in raw_selectors.split(","):
            selector = selector.strip()
            if selector:
                if selector in rules:
                    rules[selector].update(props)
                else:
                    rules[selector] = dict(props)

    return rules


def to_px(value: str, base_px: float = _BASE_FONT_PX) -> Optional[float]:
    """Convert a CSS length string to pixels. Returns None if not a valid length."""
    if not value:
        return None
    v = value.strip().lower()
    if v == "0":
        return 0.0
    if v in ("none", "auto", "inherit", "initial", "normal"):
        return None
    try:
        if v.endswith("px"):
            return float(v[:-2])
        if v.endswith("rem"):
            return float(v[:-3]) * base_px
        if v.endswith("em"):
            return float(v[:-2]) * base_px
        if v.endswith("pt"):
            return float(v[:-2]) * (4.0 / 3.0)
        if v.endswith("%"):
            return float(v[:-1]) * base_px / 100.0
    except ValueError:
        pass
    return None


def parse_shorthand_padding(padding: str) -> tuple[float, float, float, float]:
    """
    Parse a CSS padding/margin shorthand into (top, right, bottom, left) pixels.
    Returns (0,0,0,0) for empty or unparseable values.
    """
    parts = padding.split()
    values = [to_px(p) or 0.0 for p in parts if p]
    if len(values) == 1:
        v = values[0]
        return v, v, v, v
    if len(values) == 2:
        return values[0], values[1], values[0], values[1]
    if len(values) == 3:
        return values[0], values[1], values[2], values[1]
    if len(values) >= 4:
        return values[0], values[1], values[2], values[3]
    return 0.0, 0.0, 0.0, 0.0


def get_padding(styles: dict[str, str]) -> tuple[float, float, float, float]:
    """Resolve padding from a styles dict, letting individual sides override the shorthand."""
    top, right, bottom, left = parse_shorthand_padding(styles.get("padding", ""))
    t = to_px(styles.get("padding-top", ""))
    r = to_px(styles.get("padding-right", ""))
    b = to_px(styles.get("padding-bottom", ""))
    ll = to_px(styles.get("padding-left", ""))
    return (
        t if t is not None else top,
        r if r is not None else right,
        b if b is not None else bottom,
        ll if ll is not None else left,
    )


def normalize_color(color: str) -> Optional[str]:
    """Return a lowercase 6-digit hex colour string, or None if unparseable."""
    if not color:
        return None
    c = color.strip().lower()

    if c.startswith("#"):
        h = c[1:]
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        if len(h) == 6 and all(ch in "0123456789abcdef" for ch in h):
            return "#" + h

    m = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", c)
    if m:
        r, g, b = (int(x) for x in m.groups())
        return f"#{r:02x}{g:02x}{b:02x}"

    return _NAMED_COLORS.get(c)


def parse_font_families(font_family: str) -> list[str]:
    """Extract named font families, skipping generic keywords."""
    families: list[str] = []
    for part in font_family.split(","):
        name = part.strip().strip('"').strip("'").strip()
        if name and name.lower() not in _GENERIC_FONT_KEYWORDS:
            families.append(name)
    return families


def parse_inline_style(style_attr: str) -> dict[str, str]:
    """Parse an HTML inline style attribute into a {property: value} dict."""
    result: dict[str, str] = {}
    for decl in style_attr.split(";"):
        if ":" in decl:
            prop, _, value = decl.partition(":")
            result[prop.strip().lower()] = value.strip()
    return result


def parse_media_breakpoints(css_text: str) -> list[int]:
    """Extract pixel widths from @media min-width/max-width queries."""
    widths: set[int] = set()
    for m in re.finditer(
        r"@media[^{]*(?:max-width|min-width)\s*:\s*(\d+)px", css_text, re.IGNORECASE
    ):
        widths.add(int(m.group(1)))
    return sorted(widths)


def has_hover_rules(css_text: str) -> bool:
    """Return True if any :hover pseudo-class rule exists in the CSS."""
    return bool(re.search(r":hover\s*\{", css_text))


def has_transition_rules(css_text: str) -> bool:
    """Return True if any CSS transition or @keyframes animation is defined."""
    return bool(re.search(r"\btransition\s*:|@keyframes\b|animation\s*:", css_text))


def has_focus_outline_removed(css_text: str) -> bool:
    """Return True if outline is set to none/0 without a replacement focus style."""
    stripped = re.sub(r"/\*.*?\*/", "", css_text, flags=re.DOTALL)
    return bool(re.search(r"outline\s*:\s*(?:none|0)\s*[;!}]", stripped))


def parse_font_faces(css_text: str) -> list[str]:
    """Return font-family names declared via @font-face blocks."""
    names: list[str] = []
    for m in re.finditer(r"@font-face\s*\{([^}]*)\}", css_text, re.DOTALL):
        fm = re.search(r"font-family\s*:\s*['\"]?([^;'\"]+)['\"]?\s*;", m.group(1))
        if fm:
            names.append(fm.group(1).strip().strip("'\""))
    return names


def has_font_display(css_text: str) -> bool:
    """Return True if at least one @font-face block declares font-display."""
    for m in re.finditer(r"@font-face\s*\{([^}]*)\}", css_text, re.DOTALL):
        if re.search(r"font-display\s*:", m.group(1)):
            return True
    return False
