"""Tests for backend/analyzers/content_signals.py and new css_parser helpers."""
from __future__ import annotations

from bs4 import BeautifulSoup

from backend.analyzers.content_signals import extract
from backend.analyzers.css_parser import (
    has_font_display,
    parse_font_faces,
    parse_media_breakpoints,
)


def _extract(html: str, css: str = "") -> dict:
    soup = BeautifulSoup(html, "html.parser")
    return extract(soup, css)


class TestViewportMeta:
    def test_detects_present(self):
        r = _extract("<html><head><meta name='viewport' content='width=device-width'></head></html>")
        assert r["has_viewport_meta"] is True

    def test_detects_absent(self):
        r = _extract("<html><head></head></html>")
        assert r["has_viewport_meta"] is False

    def test_case_insensitive(self):
        r = _extract("<meta name='VIEWPORT' content='width=device-width'>")
        assert r["has_viewport_meta"] is True


class TestImages:
    def test_detects_alt_present(self):
        r = _extract("<img src='a.png' alt='desc'>")
        assert r["images"][0]["has_alt"] is True

    def test_detects_alt_missing(self):
        r = _extract("<img src='a.png'>")
        assert r["images"][0]["has_alt"] is False

    def test_detects_srcset(self):
        r = _extract("<img src='a.png' alt='' srcset='a-2x.png 2x'>")
        assert r["images"][0]["has_srcset"] is True

    def test_detects_width_height(self):
        r = _extract("<img src='a.png' alt='' width='200' height='100'>")
        assert r["images"][0]["has_width"] is True
        assert r["images"][0]["has_height"] is True

    def test_missing_dimensions(self):
        r = _extract("<img src='a.png' alt=''>")
        assert r["images"][0]["has_width"] is False
        assert r["images"][0]["has_height"] is False

    def test_no_images(self):
        r = _extract("<p>no images</p>")
        assert r["images"] == []


class TestTrustSignals:
    def test_detects_testimonial_class(self):
        r = _extract("<div class='testimonial'>Great product!</div>")
        assert r["has_testimonials"] is True

    def test_detects_review_class(self):
        r = _extract("<div class='review'>5 stars</div>")
        assert r["has_testimonials"] is True

    def test_no_trust_signals(self):
        r = _extract("<div class='hero'><h1>Welcome</h1></div>")
        assert r["has_testimonials"] is False

    def test_trust_count_includes_badge(self):
        r = _extract("<div class='trust-badge'>SSL Secure</div>")
        assert r["trust_signal_count"] >= 1


class TestCtaTexts:
    def test_collects_button_text(self):
        r = _extract("<button>Start Free Trial</button>")
        assert "start free trial" in r["cta_texts"]

    def test_collects_link_text(self):
        r = _extract("<a href='/pricing'>See Pricing</a>")
        assert "see pricing" in r["cta_texts"]

    def test_empty_with_no_buttons_links(self):
        r = _extract("<p>just text</p>")
        assert r["cta_texts"] == []

    def test_input_value_collected(self):
        r = _extract("<input type='submit' value='Sign Up'>")
        assert "sign up" in r["cta_texts"]


class TestHeroSection:
    def test_detects_hero_class(self):
        r = _extract("<section class='hero'><h1>Welcome</h1><p>Description here</p></section>")
        assert r["has_hero"] is True

    def test_hero_word_count(self):
        r = _extract("<section class='hero'><h1>Hello</h1><p>World this is text</p></section>")
        assert r["hero_word_count"] >= 3

    def test_no_hero_class(self):
        r = _extract("<div class='content'><p>no hero here</p></div>")
        assert r["has_hero"] is False


class TestErrorStates:
    def test_detects_aria_invalid(self):
        r = _extract("<input aria-invalid='true'>")
        assert r["has_error_states"] is True

    def test_detects_error_class(self):
        r = _extract("<div class='error'>Something went wrong</div>")
        assert r["has_error_states"] is True

    def test_detects_is_invalid_class(self):
        r = _extract("<input class='is-invalid'>")
        assert r["has_error_states"] is True

    def test_no_error_states(self):
        r = _extract("<form><input type='text'></form>")
        assert r["has_error_states"] is False


class TestFormFieldCounts:
    def test_counts_form_fields(self):
        r = _extract("""
            <form>
              <input type='text'><input type='email'><textarea></textarea>
            </form>
        """)
        assert r["form_field_counts"] == [3]

    def test_excludes_hidden_and_submit(self):
        r = _extract("""
            <form>
              <input type='text'><input type='hidden'><input type='submit'>
            </form>
        """)
        assert r["form_field_counts"] == [1]

    def test_multiple_forms(self):
        r = _extract("""
            <form><input type='text'><input type='email'></form>
            <form><input type='text'></form>
        """)
        assert sorted(r["form_field_counts"]) == [1, 2]

    def test_empty_form_excluded(self):
        r = _extract("<form></form>")
        assert r["form_field_counts"] == []


class TestPricingSection:
    def test_detects_pricing_class(self):
        r = _extract("<section class='pricing'><h2>Plans</h2></section>")
        assert r["has_pricing_section"] is True

    def test_detects_price_in_id(self):
        r = _extract("<div id='pricing-table'>...</div>")
        assert r["has_pricing_section"] is True

    def test_no_pricing(self):
        r = _extract("<div class='dashboard'><p>data</p></div>")
        assert r["has_pricing_section"] is False


class TestSkipLink:
    def test_detects_skip_link(self):
        r = _extract("<a href='#main' class='skip-link'>Skip to main content</a>")
        assert r["has_skip_link"] is True

    def test_no_skip_link(self):
        r = _extract("<a href='/home'>Home</a>")
        assert r["has_skip_link"] is False


class TestMediaBreakpoints:
    def test_parses_max_width(self):
        css = "@media (max-width: 768px) { body { font-size: 14px; } }"
        assert parse_media_breakpoints(css) == [768]

    def test_parses_min_width(self):
        css = "@media (min-width: 1024px) { .container { max-width: 960px; } }"
        assert parse_media_breakpoints(css) == [1024]

    def test_parses_multiple(self):
        css = "@media (max-width: 768px) {} @media (min-width: 1200px) {}"
        bps = parse_media_breakpoints(css)
        assert 768 in bps and 1200 in bps

    def test_returns_empty_when_none(self):
        assert parse_media_breakpoints("body { color: red; }") == []


class TestFontFaceHelpers:
    def test_detects_font_face(self):
        css = "@font-face { font-family: 'Inter'; src: url('inter.woff2'); }"
        assert parse_font_faces(css) == ["Inter"]

    def test_multiple_font_faces(self):
        css = """
            @font-face { font-family: 'Roboto'; src: url('r.woff2'); }
            @font-face { font-family: 'Poppins'; src: url('p.woff2'); }
        """
        names = parse_font_faces(css)
        assert "Roboto" in names and "Poppins" in names

    def test_has_font_display_true(self):
        css = "@font-face { font-family: 'Inter'; font-display: swap; src: url('i.woff2'); }"
        assert has_font_display(css) is True

    def test_has_font_display_false(self):
        css = "@font-face { font-family: 'Inter'; src: url('i.woff2'); }"
        assert has_font_display(css) is False

    def test_no_font_face(self):
        assert parse_font_faces("body { font-family: Arial; }") == []
        assert has_font_display("body { font-family: Arial; }") is False
