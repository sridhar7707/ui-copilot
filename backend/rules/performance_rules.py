"""
Performance rules — detect HTML/CSS signals that hurt page load speed and
Core Web Vitals without requiring a real browser: missing font-display,
images without alt/dimensions/srcset, and absent responsive breakpoints.
"""
from __future__ import annotations

from backend.models.issue import Category, Issue, Severity

_CAT = Category.PERFORMANCE


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    t = thresholds.get("performance", {})
    issues: list[Issue] = []

    _check_font_display(parsed_page, issues)
    _check_image_alt(parsed_page, issues)
    _check_image_dimensions(parsed_page, issues)
    _check_responsive_images(parsed_page, issues)
    _check_mobile_breakpoints(parsed_page, t, issues)

    return issues


# ── P1 — missing font-display ─────────────────────────────────────────────────

def _check_font_display(parsed_page: dict, issues: list[Issue]) -> None:
    web_fonts = parsed_page.get("web_fonts", [])
    has_display = parsed_page.get("has_font_display", False)

    if web_fonts and not has_display:
        issues.append(Issue(
            rule_id="P1_missing_font_display",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.90,
            message=(
                f"{len(web_fonts)} custom font(s) loaded via @font-face "
                f"({', '.join(web_fonts[:3])}) without font-display declaration."
            ),
            recommendation=(
                "Add `font-display: swap;` to every @font-face block. "
                "This renders text immediately with a fallback font while the custom "
                "font loads, eliminating Flash of Invisible Text (FOIT)."
            ),
            evidence=f"web_fonts={web_fonts[:3]}, has_font_display=False",
            estimated_time="10 minutes",
            why=(
                "Without font-display, browsers block text rendering until the font file "
                "downloads — causing FOIT (invisible text for 0–3 seconds). "
                "font-display: swap shows fallback text instantly and swaps in the web font "
                "when ready. Google's Lighthouse audit flags this, and it directly impacts "
                "First Contentful Paint (FCP) and Core Web Vitals scores."
            ),
            references=["MDN font-display", "Google Lighthouse", "web.dev/font-display"],
        ))


# ── P2 — images missing alt text ─────────────────────────────────────────────

def _check_image_alt(parsed_page: dict, issues: list[Issue]) -> None:
    images = parsed_page.get("images", [])
    missing_alt = [img for img in images if not img.get("has_alt")]

    if missing_alt:
        issues.append(Issue(
            rule_id="P2_missing_image_alt",
            category=Category.ACCESSIBILITY,  # SEO + a11y overlap, primary is accessibility
            severity=Severity.HIGH,
            confidence=0.95,
            message=(
                f"{len(missing_alt)} image(s) missing alt attribute. "
                "Screen readers will announce the filename; search engines can't index the content."
            ),
            recommendation=(
                "Add descriptive alt text to every informational image: "
                "alt='Bar chart showing Q3 revenue growth of 42%'. "
                "For purely decorative images use alt='' (empty string)."
            ),
            evidence=f"images_missing_alt={len(missing_alt)}, total_images={len(images)}",
            estimated_time="30 minutes",
            why=(
                "Alt text is the single most impactful accessibility improvement for "
                "image-heavy pages. Screen readers read it aloud; without it users hear "
                "'image.png' or nothing. Google also uses alt text for image search indexing "
                "— missing alt text is a direct SEO penalty. WCAG 1.1.1 (Level A)."
            ),
            references=["WCAG 1.1.1", "Google Image Best Practices", "WebAIM"],
        ))


# ── P3 — images missing explicit dimensions (CLS) ────────────────────────────

def _check_image_dimensions(parsed_page: dict, issues: list[Issue]) -> None:
    images = parsed_page.get("images", [])
    no_dims = [
        img for img in images
        if not img.get("has_width") or not img.get("has_height")
    ]

    if no_dims:
        issues.append(Issue(
            rule_id="P3_layout_shift_images",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.85,
            message=(
                f"{len(no_dims)} image(s) missing explicit width/height attributes — "
                "causes Cumulative Layout Shift (CLS) as content jumps when images load."
            ),
            recommendation=(
                "Add width and height attributes to every <img> matching the image's "
                "natural aspect ratio: <img src='...' width='800' height='450' alt='...'>. "
                "CSS will still respect max-width: 100%; the browser reserves space before load."
            ),
            evidence=f"images_no_dimensions={len(no_dims)}, total_images={len(images)}",
            estimated_time="20 minutes",
            why=(
                "Without dimensions, the browser doesn't know how much space to reserve "
                "for an image — content below the image shifts down when it loads (CLS). "
                "CLS above 0.1 is a Core Web Vitals failure and directly impacts "
                "Google Search ranking. Layout shift is also jarring for users — "
                "they may click the wrong element as the page reflows."
            ),
            references=["web.dev/cls", "Google Core Web Vitals", "MDN Aspect Ratio Box"],
        ))


# ── P4 — responsive images (srcset) ──────────────────────────────────────────

def _check_responsive_images(parsed_page: dict, issues: list[Issue]) -> None:
    images = parsed_page.get("images", [])
    no_srcset = [img for img in images if not img.get("has_srcset")]

    if len(no_srcset) >= 2:
        issues.append(Issue(
            rule_id="P4_missing_srcset",
            category=_CAT,
            severity=Severity.LOW,
            confidence=0.75,
            message=(
                f"{len(no_srcset)} image(s) lack srcset — mobile users download "
                "full desktop-size images, wasting bandwidth and slowing load time."
            ),
            recommendation=(
                "Add srcset with multiple resolutions: "
                "srcset='img-400.jpg 400w, img-800.jpg 800w, img-1200.jpg 1200w' "
                "sizes='(max-width: 600px) 400px, 800px'. "
                "Tools like Sharp or Cloudinary can auto-generate responsive variants."
            ),
            evidence=f"images_no_srcset={len(no_srcset)}, total_images={len(images)}",
            estimated_time="2 hours",
            why=(
                "A 2MB desktop hero image served to a 375px phone wastes ~1.8MB of data. "
                "On 4G, that's an extra 1–2 second delay. srcset lets the browser pick "
                "the right image for the viewport — a critical optimisation for mobile "
                "users who make up 60%+ of web traffic. Google Lighthouse flags this as "
                "'Serve images in next-gen formats' and 'Properly size images'."
            ),
            references=["MDN Responsive Images", "Google Lighthouse", "web.dev/uses-responsive-images"],
        ))


# ── P5 — no responsive CSS breakpoints ───────────────────────────────────────

def _check_mobile_breakpoints(parsed_page: dict, t: dict, issues: list[Issue]) -> None:
    breakpoints = parsed_page.get("media_query_breakpoints", [])
    required = t.get("required_breakpoints", [768])

    missing = [bp for bp in required if not any(abs(b - bp) <= 64 for b in breakpoints)]

    if missing:
        issues.append(Issue(
            rule_id="P5_missing_breakpoints",
            category=_CAT,
            severity=Severity.HIGH,
            confidence=0.80,
            message=(
                f"No @media query found near {missing}px breakpoint(s). "
                "The layout may not adapt for mobile/tablet viewports."
            ),
            recommendation=(
                f"Add @media (max-width: {missing[0]}px) rules to adapt typography, "
                "layout, and spacing for smaller screens. "
                "Minimum: one breakpoint at 768px (tablet) and one at 480px (phone)."
            ),
            evidence=f"detected_breakpoints={breakpoints}, missing={missing}",
            estimated_time="3 hours",
            why=(
                "60%+ of global web traffic is on mobile. A page without @media queries "
                "renders its desktop layout on phones — creating the horizontal-overflow, "
                "tiny-text, and overlapping-element issues that drive immediate bounce. "
                "Google's mobile-first indexing means a non-responsive page ranks lower "
                "in search regardless of its desktop score."
            ),
            references=["Google Mobile-First Indexing", "MDN Responsive Design", "StatCounter Mobile Traffic"],
        ))
