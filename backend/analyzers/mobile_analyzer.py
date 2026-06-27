"""
Module 15 — Mobile Analyzer.

Rules for responsive layout, touch target size, overflow handling,
mobile navigation patterns, spacing, and font sizing.

Uses the same parsed_page structure as all other analyzers.
Fires when viewport meta is absent or when mobile-relevant signals exist.
"""
from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    t = thresholds.get("mobile", {})
    bt = thresholds.get("buttons", {})
    issues: list[Issue] = []

    _check_viewport_meta(parsed_page, issues)
    _check_touch_targets(parsed_page, t, bt, issues)
    _check_font_size(parsed_page, t, issues)
    _check_horizontal_overflow(parsed_page, issues)
    _check_table_overflow(parsed_page, issues)
    _check_fixed_widths(parsed_page, t, issues)

    return issues


# ── rule implementations ──────────────────────────────────────────────────────

def _check_viewport_meta(parsed_page: dict, issues: list[Issue]) -> None:
    if parsed_page.get("has_viewport_meta") is False:
        issues.append(Issue(
            rule_id="MB1_missing_viewport_meta",
            category=Category.ACCESSIBILITY,
            severity=Severity.CRITICAL,
            confidence=0.99,
            message=(
                "No <meta name='viewport'> tag detected — the page will render "
                "at desktop width on mobile, making it completely unusable on phones."
            ),
            recommendation=(
                "Add to <head>: "
                "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            ),
            evidence="has_viewport_meta=False",
            estimated_time="2 minutes",
            why=(
                "Without the viewport meta tag, mobile browsers render your page at "
                "~980px and scale it down — text becomes unreadable without pinching. "
                "This is the #1 mobile usability failure and disqualifies the page from "
                "Google's mobile-first index. It takes 30 seconds to fix."
            ),
            references=["MDN Web Docs", "Google Search Central", "WCAG 1.4.4"],
        ))


def _check_touch_targets(parsed_page: dict, t: dict, bt: dict,
                          issues: list[Issue]) -> None:
    min_px = t.get("min_touch_target_px", bt.get("min_touch_target_px", 44))
    buttons = parsed_page.get("buttons", [])
    small = [
        b for b in buttons
        if _button_height(b) < min_px
    ]
    if small:
        smallest = min(_button_height(b) for b in small)
        issues.append(Issue(
            rule_id="MB2_small_touch_targets",
            category=Category.ACCESSIBILITY,
            severity=Severity.HIGH,
            confidence=0.85,
            message=(
                f"{len(small)} button(s) have height < {min_px}px "
                f"(smallest: {smallest:.0f}px) — too small to tap reliably on mobile."
            ),
            recommendation=(
                f"Set min-height: {min_px}px on all interactive elements. "
                "Add padding rather than increasing font size to reach the target size."
            ),
            evidence=f"small_buttons={len(small)}, min_height={smallest:.0f}px",
            estimated_time="30 minutes",
            why=(
                "The average adult fingertip covers 44–57px. Targets smaller than 44px "
                "cause tap errors — users hit the wrong element or miss entirely. "
                "WCAG 2.5.8 (Level AA) requires a minimum 24px target; Apple HIG and "
                "Material Design both recommend 44–48px for primary actions."
            ),
            references=["WCAG 2.1 SC 2.5.8", "Apple HIG", "Material Design"],
        ))


def _check_font_size(parsed_page: dict, t: dict, issues: list[Issue]) -> None:
    min_px = t.get("min_font_size_px", 14)
    body_size = parsed_page.get("body_font_size_px")
    if body_size is not None and body_size < min_px:
        issues.append(Issue(
            rule_id="MB3_small_body_font",
            category=Category.TYPOGRAPHY,
            severity=Severity.HIGH,
            confidence=0.90,
            message=(
                f"Body font size ({body_size:.0f}px) is below the mobile minimum "
                f"of {min_px}px — text will be hard to read on small screens."
            ),
            recommendation=(
                f"Set font-size: {min_px}px (preferably 16px) on body for mobile. "
                "Use a media query: @media (max-width: 768px) {{ body {{ font-size: 16px; }} }}"
            ),
            evidence=f"body_font_size_px={body_size:.0f}",
            estimated_time="10 minutes",
            why=(
                "Sub-14px text forces users to zoom on mobile — breaking layout and "
                "interrupting reading flow. iOS Safari automatically bumps text below "
                "certain sizes (causing unexpected zoom), and Google's mobile-friendliness "
                "test flags small text as a top issue."
            ),
            references=["Google Mobile-Friendly Test", "iOS Safari Text Inflation", "WCAG 1.4.4"],
        ))


def _check_horizontal_overflow(parsed_page: dict, issues: list[Issue]) -> None:
    if parsed_page.get("has_horizontal_overflow") is True:
        issues.append(Issue(
            rule_id="MB4_horizontal_overflow",
            category=Category.COMPONENT_QUALITY,
            severity=Severity.HIGH,
            confidence=0.80,
            message=(
                "Horizontal scrolling detected — content overflows the viewport width "
                "on mobile, breaking the layout."
            ),
            recommendation=(
                "Add overflow-x: hidden to body and ensure no element has a fixed "
                "width wider than the viewport. Use max-width: 100% on images and tables."
            ),
            evidence="has_horizontal_overflow=True",
            estimated_time="1 hour",
            why=(
                "Horizontal scrolling on mobile is a critical layout failure — users "
                "expect vertical-only scrolling on phones. It signals that the page was "
                "not designed for mobile and causes immediate abandonment. "
                "Google's CWV audit penalizes layout shift caused by overflow."
            ),
            references=["Google Core Web Vitals", "MDN overflow-x"],
        ))


def _check_table_overflow(parsed_page: dict, issues: list[Issue]) -> None:
    tables = parsed_page.get("tables", [])
    wide = [t for t in tables if t.get("column_count", 0) > 4]
    if wide:
        issues.append(Issue(
            rule_id="MB5_table_overflow_mobile",
            category=Category.COMPONENT_QUALITY,
            severity=Severity.MEDIUM,
            confidence=0.80,
            message=(
                f"{len(wide)} table(s) with more than 4 columns will overflow on "
                "mobile screens without a responsive wrapper."
            ),
            recommendation=(
                "Wrap tables in overflow-x: auto. On small screens, consider a "
                "card-based list view instead of a wide table — one row per card."
            ),
            evidence=f"wide_tables={len(wide)}",
            estimated_time="45 minutes",
            why=(
                "Wide tables are the leading cause of horizontal overflow on mobile. "
                "A 6-column table at 80px per column is already 480px — wider than most "
                "phones. Responsive tables (scroll-in-container or collapsed card view) "
                "are a standard pattern in every major design system."
            ),
            references=["Bootstrap Responsive Tables", "Material Design", "GOV.UK"],
        ))


def _check_fixed_widths(parsed_page: dict, t: dict,
                         issues: list[Issue]) -> None:
    max_w = t.get("max_content_width_px", 480)
    cards = parsed_page.get("cards", [])
    fixed = [
        c for c in cards
        if c.get("width_px") and c["width_px"] > max_w
    ]
    if fixed:
        issues.append(Issue(
            rule_id="MB6_fixed_width_cards",
            category=Category.COMPONENT_QUALITY,
            severity=Severity.MEDIUM,
            confidence=0.75,
            message=(
                f"{len(fixed)} card(s) have fixed pixel widths greater than {max_w}px "
                "— they will overflow or get clipped on mobile."
            ),
            recommendation=(
                "Replace fixed px widths with max-width + width: 100%. "
                "Use CSS Grid or Flexbox with flex-wrap: wrap for card layouts."
            ),
            evidence=f"fixed_cards={len(fixed)}, max_content_width={max_w}px",
            estimated_time="30 minutes",
            why=(
                "Fixed-width elements are the root cause of most mobile layout breaks. "
                "A 600px-wide card on a 375px phone either clips, overlaps, or forces "
                "horizontal scroll. Fluid layouts (width: 100%, max-width: Xpx) work "
                "across all screen sizes without breakpoints."
            ),
            references=["MDN Flexible Box Layout", "CSS Grid", "Bootstrap Grid"],
        ))


# ── helpers ───────────────────────────────────────────────────────────────────

def _button_height(btn: dict) -> float:
    if btn.get("height_px"):
        return float(btn["height_px"])
    pt = btn.get("padding_top_px", 0) or 0
    pb = btn.get("padding_bottom_px", 0) or 0
    fs = btn.get("font_size_px", 16) or 16
    return pt + fs * 1.2 + pb
