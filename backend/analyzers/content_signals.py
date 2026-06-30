"""
Content signals extractor — produces the new ParsedPage fields that support
Conversion, UX Quality, Performance, and Interactivity rules.

Called by html_analyzer.parse() and merged into the ParsedPage dict.
"""
from __future__ import annotations

from bs4 import BeautifulSoup, Tag

from backend.analyzers.css_parser import (
    has_focus_outline_removed,
    has_font_display,
    has_hover_rules,
    has_transition_rules,
    parse_font_faces,
    parse_media_breakpoints,
)

_TRUST_KEYWORDS = frozenset({
    "testimonial", "review", "rating", "stars", "trust", "secure", "ssl",
    "verified", "badge", "guarantee", "certification", "award", "payment",
    "visa", "mastercard", "paypal", "stripe", "clients", "partner",
    "customers", "users", "trusted",
})

_HERO_KEYWORDS = frozenset({"hero", "jumbotron", "banner", "splash", "masthead", "intro"})

_WEAK_CTA_PHRASES = frozenset({
    "click here", "click", "here", "submit", "learn more", "read more",
    "more", "go", "ok", "button", "next", "continue", "send", "enter",
    "view", "see", "check", "find out",
})

_ERROR_CLASS_KEYWORDS = frozenset({"error", "invalid", "danger", "alert", "is-invalid"})

_EMPTY_STATE_KEYWORDS = frozenset({"empty", "no-data", "no-results", "placeholder", "blank"})

_FORM_KEYWORDS = frozenset({"signup", "sign-up", "register", "checkout", "contact", "login", "subscribe"})


def extract(soup: BeautifulSoup, raw_css: str) -> dict:
    """Return a dict of all new ParsedPage fields derived from HTML + CSS."""
    return {
        "has_viewport_meta": _viewport_meta(soup),
        "has_horizontal_overflow": _horizontal_overflow(soup, raw_css),
        "images": _images(soup),
        "media_query_breakpoints": parse_media_breakpoints(raw_css),
        "has_hover_styles": has_hover_rules(raw_css),
        "has_transitions": has_transition_rules(raw_css),
        "has_font_display": has_font_display(raw_css),
        "web_fonts": parse_font_faces(raw_css),
        "trust_signal_count": _trust_signal_count(soup),
        "has_testimonials": _has_testimonials(soup),
        "cta_texts": _cta_texts(soup),
        "has_hero": _has_hero(soup),
        "hero_word_count": _hero_word_count(soup),
        "has_error_states": _has_error_states(soup),
        "has_empty_states": _has_empty_states(soup),
        "has_focus_outline_removed": has_focus_outline_removed(raw_css),
        "form_field_counts": _form_field_counts(soup),
        "page_word_count": _page_word_count(soup),
        "has_pricing_section": _has_pricing_section(soup),
        "has_skip_link": _has_skip_link(soup),
    }


# ── viewport / overflow ───────────────────────────────────────────────────────

def _viewport_meta(soup: BeautifulSoup) -> bool:
    for meta in soup.find_all("meta"):
        if isinstance(meta, Tag) and meta.get("name", "").lower() == "viewport":
            return True
    return False


def _horizontal_overflow(soup: BeautifulSoup, raw_css: str) -> bool:
    import re
    if re.search(r"overflow-x\s*:\s*(?:hidden|scroll|auto)", raw_css):
        return False
    for el in soup.find_all(style=True):
        if not isinstance(el, Tag):
            continue
        style = el.get("style", "")
        if "overflow-x" in style:
            return False
        import re as _re
        m = _re.search(r"\bwidth\s*:\s*(\d+)px", style)
        if m and int(m.group(1)) > 768:
            return True
    return False


# ── images ────────────────────────────────────────────────────────────────────

def _images(soup: BeautifulSoup) -> list[dict]:
    result = []
    for img in soup.find_all("img"):
        if not isinstance(img, Tag):
            continue
        style = img.get("style", "")
        result.append({
            "src": str(img.get("src", ""))[:80],
            "has_alt": img.has_attr("alt"),
            "alt_text": str(img.get("alt", ""))[:60],
            "has_srcset": img.has_attr("srcset"),
            "has_width": img.has_attr("width") or "width" in style,
            "has_height": img.has_attr("height") or "height" in style,
        })
    return result


# ── trust signals ─────────────────────────────────────────────────────────────

def _trust_signal_count(soup: BeautifulSoup) -> int:
    count = 0
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        combined = (
            " ".join(el.get("class", [])).lower()
            + " " + (el.get("id", "") or "").lower()
        )
        if any(kw in combined for kw in _TRUST_KEYWORDS):
            count += 1
    return count


def _has_testimonials(soup: BeautifulSoup) -> bool:
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        combined = " ".join(el.get("class", [])).lower() + " " + (el.get("id", "") or "").lower()
        if "testimonial" in combined or "review" in combined:
            return True
    return False


# ── CTA text analysis ─────────────────────────────────────────────────────────

def _cta_texts(soup: BeautifulSoup) -> list[str]:
    texts: list[str] = []
    for el in soup.find_all(["button", "a", "input"]):
        if not isinstance(el, Tag):
            continue
        if el.name == "input":
            t = (el.get("value", "") or "").strip().lower()
        else:
            t = el.get_text(strip=True).lower()
        if t and len(t) <= 60:
            texts.append(t)
    return texts[:50]


# ── hero section ──────────────────────────────────────────────────────────────

def _find_hero_el(soup: BeautifulSoup) -> Tag | None:
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        combined = " ".join(el.get("class", [])).lower() + " " + (el.get("id", "") or "").lower()
        if any(kw in combined for kw in _HERO_KEYWORDS):
            return el
    return None


def _has_hero(soup: BeautifulSoup) -> bool:
    return _find_hero_el(soup) is not None


def _hero_word_count(soup: BeautifulSoup) -> int:
    el = _find_hero_el(soup)
    if el is None:
        # fall back to first <section> or <header>
        el = soup.find(["section", "header"])
    if el is None or not isinstance(el, Tag):
        return 0
    return len(el.get_text(separator=" ").split())


# ── error / empty states ──────────────────────────────────────────────────────

def _has_error_states(soup: BeautifulSoup) -> bool:
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        if el.get("aria-invalid") or el.get("aria-errormessage"):
            return True
        classes = {c.lower() for c in el.get("class", [])}
        if any(kw in cls for cls in classes for kw in _ERROR_CLASS_KEYWORDS):
            return True
    return False


def _has_empty_states(soup: BeautifulSoup) -> bool:
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        combined = " ".join(el.get("class", [])).lower() + " " + (el.get("id", "") or "").lower()
        if any(kw in combined for kw in _EMPTY_STATE_KEYWORDS):
            return True
    return False


# ── form analysis ─────────────────────────────────────────────────────────────

def _form_field_counts(soup: BeautifulSoup) -> list[int]:
    """Return a list of field counts, one per <form> element on the page."""
    skip_types = {"hidden", "submit", "button", "reset", "image"}
    counts: list[int] = []
    for form in soup.find_all("form"):
        if not isinstance(form, Tag):
            continue
        fields = [
            el for el in form.find_all(["input", "textarea", "select"])
            if isinstance(el, Tag)
            and not (el.name == "input" and el.get("type", "text").lower() in skip_types)
        ]
        if fields:
            counts.append(len(fields))
    return counts


# ── page / content ────────────────────────────────────────────────────────────

def _page_word_count(soup: BeautifulSoup) -> int:
    return len(soup.get_text(separator=" ").split())


def _has_pricing_section(soup: BeautifulSoup) -> bool:
    for el in soup.find_all(True):
        if not isinstance(el, Tag):
            continue
        combined = " ".join(el.get("class", [])).lower() + " " + (el.get("id", "") or "").lower()
        if "pricing" in combined or "price" in combined or "plan" in combined:
            return True
    return False


def _has_skip_link(soup: BeautifulSoup) -> bool:
    for a in soup.find_all("a"):
        if not isinstance(a, Tag):
            continue
        href = (a.get("href", "") or "").lower()
        text = a.get_text(strip=True).lower()
        if "skip" in text and href.startswith("#"):
            return True
    return False
