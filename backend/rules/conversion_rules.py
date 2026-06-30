"""
Conversion Optimization rules — detect patterns that hurt business outcomes
regardless of visual polish: weak CTAs, excessive form friction, missing trust
signals, unclear hero messaging, and absent pricing clarity.
"""
from __future__ import annotations

from backend.models.issue import Category, Issue, Severity

_CAT = Category.CONVERSION_OPTIMIZATION

_WEAK_CTA_PHRASES = frozenset({
    "click here", "click", "here", "submit", "learn more", "read more",
    "more", "go", "ok", "button", "see more", "view more", "find out",
    "find out more", "enter",
})

_ACTION_VERBS = frozenset({
    "start", "get", "try", "sign", "join", "create", "build", "launch",
    "download", "buy", "order", "book", "schedule", "request", "apply",
    "explore", "discover", "watch", "play", "upgrade", "activate",
})


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    t = thresholds.get("conversion", {})
    issues: list[Issue] = []

    _check_weak_cta(parsed_page, t, issues)
    _check_form_friction(parsed_page, t, issues)
    _check_trust_signals(parsed_page, t, issues)
    _check_hero_clarity(parsed_page, t, issues)
    _check_pricing_cta(parsed_page, issues)

    return issues


# ── CV1 — weak CTA text ───────────────────────────────────────────────────────

def _check_weak_cta(parsed_page: dict, t: dict, issues: list[Issue]) -> None:
    cta_texts = parsed_page.get("cta_texts", [])
    if not cta_texts:
        return

    weak = [
        txt for txt in cta_texts
        if txt.lower().strip() in _WEAK_CTA_PHRASES
    ]
    # Check if ANY CTA uses a strong action verb
    has_strong = any(
        any(verb in txt.lower() for verb in _ACTION_VERBS)
        for txt in cta_texts
    )

    if weak and not has_strong:
        issues.append(Issue(
            rule_id="CV1_weak_cta_text",
            category=_CAT,
            severity=Severity.HIGH,
            confidence=0.80,
            message=(
                f"{len(weak)} CTA(s) use generic text "
                f"({', '.join(repr(w) for w in weak[:3])}) with no strong action verb found."
            ),
            recommendation=(
                "Replace passive CTA text with outcome-oriented action verbs: "
                "'Start Free Trial', 'Get My Report', 'Join 10,000 Users'. "
                "Specific CTAs outperform generic ones by 90% on average."
            ),
            evidence=f"weak_ctas={weak[:5]}",
            estimated_time="15 minutes",
            why=(
                "CTA copy is the last thing a user reads before deciding to convert. "
                "Generic phrases like 'Submit' or 'Learn More' create uncertainty — "
                "the user doesn't know what happens next. Specific action verbs set clear "
                "expectations and increase click-through rates by 20–90% in A/B tests."
            ),
            references=["Copyhackers", "HubSpot CTA Research", "Nielsen Norman Group"],
        ))
    elif weak:
        issues.append(Issue(
            rule_id="CV1_weak_cta_text",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.75,
            message=f"{len(weak)} CTA(s) use generic text: {', '.join(repr(w) for w in weak[:3])}.",
            recommendation=(
                "Audit each generic CTA and rewrite with the user's desired outcome: "
                "'Get Access', 'Download the Guide', 'See Pricing'."
            ),
            evidence=f"weak_ctas={weak[:5]}",
            estimated_time="20 minutes",
            why=(
                "Even when strong CTAs exist on the page, weak CTAs in secondary positions "
                "reduce overall conversion confidence. Every button should feel intentional."
            ),
            references=["Copyhackers", "ConversionXL"],
        ))


# ── CV2 — form friction ───────────────────────────────────────────────────────

def _check_form_friction(parsed_page: dict, t: dict, issues: list[Issue]) -> None:
    max_fields = t.get("max_form_fields", 6)
    counts = parsed_page.get("form_field_counts", [])
    overloaded = [c for c in counts if c > max_fields]
    if overloaded:
        worst = max(overloaded)
        issues.append(Issue(
            rule_id="CV2_form_friction",
            category=_CAT,
            severity=Severity.HIGH,
            confidence=0.85,
            message=(
                f"{len(overloaded)} form(s) have more than {max_fields} fields "
                f"(worst: {worst} fields) — high friction reduces sign-ups by 50%+."
            ),
            recommendation=(
                f"Reduce to {max_fields} or fewer fields for initial sign-up/checkout. "
                "Defer optional fields (phone, company size) to onboarding or profile setup. "
                "Use progressive disclosure for multi-step flows."
            ),
            evidence=f"form_field_counts={counts}",
            estimated_time="2 hours",
            why=(
                "Every additional field in a sign-up form reduces conversion rate by ~4–10%. "
                "Experian found that reducing from 11 to 4 fields increased conversions 120%. "
                "Collect only what's needed to get the user started — gather the rest later."
            ),
            references=["Experian Form Study", "Baymard Institute", "HubSpot Blog"],
        ))


# ── CV3 — missing trust signals ───────────────────────────────────────────────

def _check_trust_signals(parsed_page: dict, t: dict, issues: list[Issue]) -> None:
    min_signals = t.get("min_trust_signals", 1)
    count = parsed_page.get("trust_signal_count", 0)
    has_testimonials = parsed_page.get("has_testimonials", False)

    if count < min_signals and not has_testimonials:
        issues.append(Issue(
            rule_id="CV3_missing_trust_signals",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.70,
            message=(
                "No trust signals detected — no testimonials, security badges, "
                "review counts, or social proof elements found."
            ),
            recommendation=(
                "Add near every primary CTA: customer count ('10,000+ users'), "
                "a testimonial quote with attribution, star ratings, "
                "security badges (SSL, SOC2), or recognisable logos of customers/partners."
            ),
            evidence=f"trust_signal_count={count}, has_testimonials={has_testimonials}",
            estimated_time="3 hours",
            why=(
                "Trust signals reduce purchase anxiety. 88% of consumers trust online "
                "reviews as much as personal recommendations (BrightLocal). "
                "A single testimonial near a CTA can increase conversion by 34% "
                "(Trustpilot case studies). First-time visitors need social proof "
                "before committing — without it, they leave to search for reviews elsewhere."
            ),
            references=["BrightLocal Consumer Review Survey", "Trustpilot", "Nielsen Trust Study"],
        ))


# ── CV4 — hero clarity ────────────────────────────────────────────────────────

def _check_hero_clarity(parsed_page: dict, t: dict, issues: list[Issue]) -> None:
    max_words = t.get("hero_max_words", 150)
    min_words = t.get("hero_min_words", 5)
    has_hero = parsed_page.get("has_hero", False)
    word_count = parsed_page.get("hero_word_count", 0)
    headings = parsed_page.get("headings", [])
    has_h1 = any(h["level"] == 1 for h in headings)

    if not has_h1:
        issues.append(Issue(
            rule_id="CV4_missing_value_proposition",
            category=_CAT,
            severity=Severity.HIGH,
            confidence=0.90,
            message="No <h1> found — the page has no primary value proposition headline.",
            recommendation=(
                "Add a clear <h1> that answers 'What does this do and why should I care?' "
                "in one sentence. E.g. 'The fastest way to turn UI audits into shipped fixes.'"
            ),
            evidence="headings_h1_count=0",
            estimated_time="30 minutes",
            why=(
                "Users scan pages in 3–5 seconds. If there's no clear headline explaining "
                "the value, 70% will bounce before reading a single paragraph. "
                "The H1 is the first thing screen readers and search engines encounter — "
                "it's the most high-leverage copy on the page."
            ),
            references=["Nielsen Norman Group", "Google Search Central", "Copyhackers"],
        ))
    elif has_hero and word_count > max_words:
        issues.append(Issue(
            rule_id="CV4_hero_word_overload",
            category=_CAT,
            severity=Severity.MEDIUM,
            confidence=0.75,
            message=(
                f"Hero section contains {word_count} words — "
                f"above the {max_words}-word threshold for scannable above-the-fold content."
            ),
            recommendation=(
                "Cut hero copy to a headline (8–12 words) + subheadline (1–2 sentences). "
                "Move supporting detail below the fold or into a 'learn more' section. "
                "Every word above the fold costs attention."
            ),
            evidence=f"hero_word_count={word_count}",
            estimated_time="1 hour",
            why=(
                "F-pattern eye-tracking studies show users read the hero heading and "
                "the first few words of the subheadline before deciding whether to scroll. "
                "Dense hero copy signals 'this will take effort to understand' and drives bounce."
            ),
            references=["Nielsen NNG Eye-Tracking", "Copyhackers", "ConversionXL"],
        ))
    elif not has_hero and word_count == 0:
        issues.append(Issue(
            rule_id="CV4_no_hero_section",
            category=_CAT,
            severity=Severity.LOW,
            confidence=0.60,
            message="No hero or introductory section detected — consider adding an above-the-fold value statement.",
            recommendation=(
                "Add a <section class='hero'> with a headline, subheadline, and primary CTA "
                "in the first viewport. Users should immediately understand what this page offers."
            ),
            evidence="has_hero=False, hero_word_count=0",
            estimated_time="2 hours",
            why=(
                "Without a clear introductory section, new visitors must hunt for context. "
                "Structured hero sections improve time-on-page and reduce bounce for cold traffic."
            ),
            references=["Nielsen NNG", "Smashing Magazine"],
        ))


# ── CV5 — pricing CTA alignment ───────────────────────────────────────────────

def _check_pricing_cta(parsed_page: dict, issues: list[Issue]) -> None:
    has_pricing = parsed_page.get("has_pricing_section", False)
    cta_texts = parsed_page.get("cta_texts", [])
    buttons = parsed_page.get("buttons", [])

    if has_pricing and not buttons:
        issues.append(Issue(
            rule_id="CV5_pricing_no_cta",
            category=_CAT,
            severity=Severity.HIGH,
            confidence=0.80,
            message="Pricing section detected but no CTA buttons found on the page.",
            recommendation=(
                "Add a clear CTA button inside or directly below the pricing section: "
                "'Get Started', 'Choose Plan', or 'Start Free Trial'. "
                "Pricing without a CTA is a dead end."
            ),
            evidence="has_pricing_section=True, buttons=[]",
            estimated_time="30 minutes",
            why=(
                "A pricing page without an adjacent CTA forces the user to scroll back "
                "to find where to sign up — every extra scroll is a drop-off risk. "
                "Baymard Institute found 69% of checkout abandonments happen because "
                "the path to purchase was unclear."
            ),
            references=["Baymard Institute Checkout Research", "ConversionXL"],
        ))
