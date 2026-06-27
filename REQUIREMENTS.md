# UICopilot — Living Requirements Document

Auto-generated and auto-updated.
Last updated: 2026-06-26 (session 2 — V1 modules completed)
Version: 1.4.0

---

## PROJECT OVERVIEW

Name: UICopilot
Type: AI UI/UX Engineering Platform
Stack: Python, FastAPI, React, SQLite, HuggingFace Spaces, Streamlit/Gradio (rapid-prototype front ends)
Purpose: Help developers analyze, score, and improve the visual and UX quality of their applications — screenshots, HTML, and CSS in — prioritized, explainable fixes out.

This is the second flagship project after TradeGenius. Same philosophy, different domain: TradeGenius doesn't just say "buy," it explains why, how much, and what to do next. UICopilot doesn't just say "your spacing is bad," it explains what's wrong, why it matters, how much it hurts the score, and exactly how to fix it.

---

## PROJECT VISION

### Mission

Help developers build beautiful, consistent, accessible user interfaces by analyzing screenshots and source code, assigning objective quality scores, identifying issues, and generating actionable improvements.

### The Positioning Shift

The original framing was "AI UI/UX Quality Analyzer" — a tool that grades a screenshot. The stronger framing, and the one this document specifies, is:

> **The AI Platform for Developers to Build Beautiful Software.**

Think SonarQube for UI/UX — but with AI recommendations, design education, and code generation built in. Not a testing tool. A developer cockpit.

### Target Users

**Primary**
- Backend developers
- Full-stack developers
- Solo founders
- AI developers (people shipping AI-wrapped products who never trained as designers)
- Internal enterprise teams

**Secondary**
- UX/UI designers
- Students
- Agencies

### Core Value Proposition

UICopilot should let a developer answer:

- How good is my UI?
- Why does it look unprofessional?
- What should I fix first?
- How can I make it look like Stripe, Linear, or Notion?
- Can AI generate the fixes?
- Is today's UI better than yesterday's?

### Design Philosophy — "Don't Make the Score the Product"

The score is a hook, not the deliverable. The actual product is the prioritized action plan underneath it:

```
UI Score: 82/100

Increase card padding from 12px to 20px       (+4 points)
Make table headers 13px uppercase             (+3 points)
Standardize primary button styling            (+2 points)
```

Every screen in the product should answer four questions:

1. How good is my UI?
2. What's hurting it the most?
3. What's the fastest way to improve it?
4. Show me exactly how to fix it.

### The Biggest Differentiator

Most UI tools answer "how does my UI look?" UICopilot answers:

> "How do I make my UI look like software built by a senior product designer?"

---

## STEP 1 — GITHUB REPOSITORY

Repository name: `ui-copilot`
Visibility: Public

**Description**

AI-powered UI/UX Engineering Platform that analyzes screenshots, HTML, CSS, and applications, scores interface quality, detects design issues, teaches best practices, and generates actionable improvements.

**Repository Topics**

```
ui, ux, ai, design-system, streamlit, gradio, react, html, css,
python, fastapi, accessibility, computer-vision, developer-tools
```

**Initial Files**

- `README.md`
- `LICENSE` (MIT)
- `CHANGELOG.md`
- `ROADMAP.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `.gitignore` (Python)

**Branch Strategy**

- `main`
- `develop`
- `feature/*`

---

## STEP 2 — HIGH-LEVEL ARCHITECTURE

```
Frontend
   ↓
FastAPI Backend
   ↓
Analysis Engine
   ├── Screenshot Analyzer
   ├── HTML Analyzer
   ├── CSS Analyzer
   ├── Component Analyzer
   ├── Accessibility Analyzer
   ├── Typography Analyzer
   ├── Spacing Analyzer
   ├── Color Analyzer
   ├── Dashboard Analyzer
   ├── Table Analyzer
   ├── Mobile Analyzer
   └── Design System Analyzer
   ↓
Recommendation Engine
   ↓
Score Engine
   ↓
Learning Engine
   ↓
Claude Prompt Generator
   ↓
SQLite (DuckDB added later for analytics, trend history, reports)
```

Layered, with strict separation of concerns: API → Services → Analyzers → Rules → Repositories. No analyzer talks directly to the database; no business logic lives in API endpoints.

---

## STEP 3 — FOLDER STRUCTURE

```
ui-copilot/
├── backend/
│   ├── api/
│   ├── services/
│   ├── analyzers/
│   ├── rules/          # YAML rule definitions — see DESIGN RULES ENGINE
│   ├── models/
│   ├── repositories/
│   └── utils/
├── frontend/
│   ├── components/
│   ├── pages/
│   └── assets/
├── tests/
├── docs/
│   ├── REQUIREMENTS.md
│   ├── specs/
│   └── adr/
├── samples/
├── reports/
├── data/
├── config/
├── scripts/
├── requirements.txt
└── README.md
```

---

## STEP 4 — VERSION 1 SCOPE

**In scope:** Screenshot, HTML, CSS analysis only. No live URL crawling, no code generation beyond CSS/prompt suggestions in V1's stretch goals.

**Explicitly out of scope for V1:**

- ❌ AI Chat
- ❌ Figma Plugin
- ❌ Live Browser Extension
- ❌ Auto Code Generation (full file rewrites)
- ❌ Multi-user Accounts
- ❌ Cloud Deployment

**Usage model:** Single-operator for V1. You and your team run the analyses directly and relay findings to clients as commentary — clients do not get direct access to the tool. This is a deliberate simplification, not a placeholder: it removes the need for authentication, multi-tenant data isolation, and concurrent-request handling, which keeps the free-tier compute footprint (HuggingFace Spaces CPU-basic) comfortably sufficient, since only one analysis ever runs at a time. Client-facing access is deferred to Version 1.5 (see `ROADMAP.md`) and should only be built once there's enough concurrent client demand to justify the added complexity — particularly around auth and data isolation, which are security-sensitive enough to deserve their own focused phase rather than being folded into V1.

---

## BUILD ORDER (PHASING)

Module 3b (Benchmark Library / embedding similarity) and the richer generation modules are **non-blocking** for shipping a useful product. Build in this order so real value lands in weeks, not months:

```
Phase 1 — Rule Engine, UI Scoring, Reports
            (no reference images needed; pure rule-based analysis)
   ↓
Phase 2 — Design System Analyzer
            (inconsistency detection across buttons/cards/tables)
   ↓
Phase 3 — Claude Prompt Generator
            (turn findings into a one-click copy/paste prompt)
   ↓
Phase 4 — Benchmark Library + Embedding Similarity
            (Module 3b — optional enhancement, not a dependency)
   ↓
Phase 5 — Auto CSS Generation, Before/After Preview
   ↓
Phase 6 — GitHub Integration
   ↓
Phase 7 — Enterprise / Client-Access Features
            (see Version 1.5 in ROADMAP.md — gated on real demand)
```

A working, valuable tool exists after Phase 1 alone. Everything after that is enhancement, not prerequisite.

---

## PRODUCT MODULES

The platform is organized into 22 modules. V1 (see Success Criteria) implements a focused subset; the rest are designed now so later modules slot in without rearchitecting.

### Module 1 — Project Management ✅ DONE

Users create projects (e.g. "TradeGenius," "Landlord Copilot," "My CRM"). Each project stores its pages, screenshots, reports, scores, and history.

### Module 2 — Page Analyzer ✅ DONE

**Inputs:** Screenshot, URL, HTML, CSS, React, Streamlit, Gradio.

**Outputs:** Overall Score, Visual Score, Accessibility Score, Professional Score, Modern Design Score, Consistency Score, Developer Score, Maintainability Score.

### Module 3 — Screenshot Analysis ✅ DONE

Detects: cards, tables, buttons, navigation, charts, typography, whitespace, colors, forms, icons, badges, progress bars, dialogs, modals, headers, footers.

Detection uses free, locally-run techniques rather than a paid vision-LLM API call:

- **Deterministic CV** (free) — OpenCV/Pillow-based layout detection, color extraction (k-means palette clustering), and spacing measurement between detected elements. Handles contrast, alignment, and palette-harmony checks with full accuracy since these are arithmetic, not judgment calls.
- **Open-source layout/component models** (free) — locally-run, CPU-friendly models (e.g. HuggingFace layout-detection models) for classifying cards/tables/buttons/nav from pixels. Narrower than a vision-LLM but accurate enough for the standard UI component vocabulary.
- **Framework fingerprinting** (free) — known CSS/visual signatures of Bootstrap, Tailwind, and Material defaults are matched against uploaded HTML/CSS (or inferred from screenshot color/shape patterns when no source is available) to flag "looks like an unstyled default."

### Module 3b — Benchmark Library & Similarity Scoring

**Status: optional enhancement, not a dependency.** Nothing in Phases 1–3 of the Build Order requires this module — it is built in Phase 4, after the Rule Engine, Design System Analyzer, and Prompt Generator already produce a useful, shippable tool. Renamed from "Reference Dataset" to **Benchmark Library**, since the latter accurately signals "curated examples of excellent (and poor) UI for comparison" rather than implying ML training infrastructure.

Approximates the "does this look professional" judgment a vision-LLM would make, without calling one or paying for one.

**Approach:** a curated local Benchmark Library of real product UI screenshots is embedded once using a free, locally-run embedding model (e.g. an open-source CLIP variant). Each new analysis embeds the uploaded screenshot the same way and scores it by similarity-to-benchmark rather than by asking a model to judge quality from scratch — converting a subjective judgment into a free distance calculation.

**Beyond pixels — compare the fuller picture when source is available.** When HTML/CSS was uploaded alongside the screenshot (which Module 2 already parses), the comparison isn't limited to image similarity. It extends to:

```
Screenshot + HTML + CSS + Component Tree + Design Tokens
   ↓
Combined Analysis
```

This produces a more specific, multi-axis similarity output rather than a single number:

```
Overall Similarity     91%
  Layout                96%
  Typography            88%
  Spacing               72%
  Colors                94%
```

This is free — it reuses parsing work Module 2 already does — and gives a far more actionable signal than image similarity alone.

**Library structure:**

```
benchmark_library/
├── excellent/
│   ├── cards/
│   ├── tables/
│   ├── dashboards/
│   ├── navigation/
│   ├── forms/
│   ├── buttons/
│   ├── charts/
│   ├── metrics/
│   ├── empty_states/
│   ├── login/
│   ├── onboarding/
│   ├── mobile/
│   └── settings/
└── poor/
    └── (same category structure)
```

Each image is paired with a JSON metadata file of the same name, e.g. `stripe_card_001.png` + `stripe_card_001.json`:

```json
{
  "id": "stripe_card_001",
  "product": "Stripe Dashboard",
  "category": "cards",
  "quality_score": 96,
  "attributes": {
    "spacing": "excellent",
    "typography": "excellent",
    "contrast": "excellent",
    "padding": 24,
    "radius": 10,
    "shadow": "light",
    "density": "comfortable"
  },
  "notes": [
    "Clear hierarchy",
    "Good use of whitespace",
    "Strong visual emphasis on KPI"
  ]
}
```

The same schema is used for the `poor/` set, with `quality_score` and `attributes` reflecting what's wrong (e.g. `"spacing": "cramped"`, `"density": "overcrowded"`) so the system has negative examples to compare against, not just positive ones.

**Why both excellent and poor examples matter:** scoring against only good benchmarks tells you "how far from great" something is. Adding labeled poor examples lets the system also recognize known anti-patterns directly — e.g. flagging that a dashboard resembles a "crowded, low-hierarchy" example, not just that it's distant from a "clean, high-hierarchy" one. This is a more specific and more actionable signal.

**Comparison-output feature:** the JSON metadata enables the "why" behind a similarity score, not just the number. Output format for a given analysis:

```
Compared against:
  Stripe Dashboard    92% similarity
  Linear               81% similarity
  GitHub               74% similarity

Main differences from closest match (Stripe):
  ✓ Better spacing needed (cramped vs. excellent)
  ✓ Larger KPI cards recommended
  ✓ Cleaner table headers needed
  ✓ Better empty-state messaging needed
```

This is generated by diffing the uploaded screenshot's inferred attributes against the closest-matching benchmark's `attributes` block — directly reusing the metadata schema above rather than requiring a separate explanation system.

**Target library size:** start at ~120 images (20 each across cards, tables, dashboards, forms, navigation, buttons) rather than waiting to gather hundreds before building anything. Expand over time as real client work produces more benchmark-quality examples — this is a living library, not a one-time deliverable.

**Sourcing — real screenshots only, kept private:** benchmark images should be genuine screenshots of real production software (tiered by recognizability and daily usage — e.g. Stripe, Linear, Notion, GitHub, Vercel, Mercury as top-tier; Atlassian, Slack, ClickUp, Airtable as secondary), gathered manually by the team. **This library is not committed to the public `ui-copilot` GitHub repository** — it lives in `data/` (already `.gitignore`d) as a private, local asset, the same way client screenshots are never committed. This avoids any copyright/redistribution concern with using real commercial product screenshots, while preserving the accuracy that comes from comparing against genuine production UI rather than synthetic approximations. AI-generated mockups may be used to **supplement** gaps in hard-to-source categories (e.g. a clean example of a "poor" empty state), but should not replace real screenshots as the primary source, since the value of the comparison feature depends on the benchmarks being genuine.

**Sizing:**

- Benchmark library: ~120 images at launch, growing over time.
- Raw benchmark images: not needed at runtime — only used once, during precompute, and kept private/local regardless.
- Stored embeddings (the only thing needed at runtime): ~3KB per image → a few hundred KB total even at launch size, well under 5MB even if the library grows into the hundreds. Negligible footprint.
- Per-user analysis data (screenshots, HTML/CSS, reports, history) is the actual long-term storage driver and scales with usage, not with this feature — this is why uploaded screenshots are not retained beyond the configured window unless explicitly saved to a project (see Security, below).

**Resource requirement:** the embedding model must be loaded once at process startup and kept resident in memory — never reloaded per-request. Under the single-operator usage model (see Step 4), this is a correctness/efficiency best practice rather than a hard requirement, since there is no concurrent load to cause memory pressure; it becomes load-bearing if/when Version 1.5 (Client Access, see `ROADMAP.md`) introduces concurrent usage.

**Explicitly deferred — community/user-feedback learning loop:** a future idea (not part of this module, not architected for yet) is letting real user uploads and accepted/rejected recommendations grow the library automatically over time, rather than relying solely on manually-curated benchmarks. This is **not built or designed into the V1 data model**. It depends on the Version 1.5 client-access world (multiple real users, accounts, volume) which hasn't been built yet, and it requires a deliberate privacy/data-retention policy decision — "anonymized" storage of user uploads is a real commitment, not a checkbox, and would need to be weighed against the existing rule that uploaded screenshots aren't retained beyond a configured window. If and when Version 1.5 ships and there's real usage volume, this is worth revisiting on purpose, with its own privacy review — not bolted on incidentally to Module 3b now.

### Module 4 — Design System Detection ✅ DONE

Automatically discovers buttons, cards, inputs, tables, badges, dialogs, colors, spacing, and typography in use, then flags inconsistency.

Example: *Buttons — 6 primary styles detected ❌ → Recommendation: reduce to one.*

### Module 5 — Scoring Engine ✅ DONE

Overall score out of 100, built from independently scored categories:

| Category | Weight |
|---|---|
| Visual Hierarchy | 20% |
| Typography | 15% |
| Spacing | 15% |
| Consistency | 15% |
| Accessibility | 15% |
| Contrast | 10% |
| Component Quality | 10% |

Extended categories (used as the model matures): Information Density, Dashboard Quality, Mobile Readiness, Performance Impact, Maintainability.

Weights and thresholds live in configuration files, not in code.

### Module 6 — Issue Detection ✅ DONE

Every issue carries: Severity, Confidence, Evidence, Screenshot Highlight, Recommendation, Estimated Improvement, Estimated Time.

```
Issue: Button Padding
Severity: High
Estimated Gain: +4
Time: 2 minutes
```

### Module 7 — Improvement Roadmap ✅ DONE

Generates Top 10 Improvements, Quick Wins, High Impact items, Easy Fixes, Accessibility Fixes, Visual Improvements, and Consistency Improvements — ranked, not just listed.

**Score-increase chaining:** fixes are sequenced by cumulative projected score, not just listed independently with isolated point estimates. Example:

```
Current               82
   ↓ Fix typography    85
   ↓ Fix spacing       89
   ↓ Fix tables        92
```

This shows the running total as each fix is applied — more motivating than a flat list of unordered "+N point" items, and it gives the developer a concrete, ordered path to a target score rather than a pile of disconnected suggestions.

### Module 8 — Learning Mode ✅ DONE

Every recommendation teaches, rather than just states the problem:

```
Problem: Typography hierarchy
Why: Users scan before reading.
Fix: Increase hero metrics to 32px.
Examples: Stripe, Linear, Notion
```

### Module 9 — Claude Prompt Generator ✅ DONE

Generates a ready-to-paste prompt summarizing the fixes needed, e.g.:

> Refactor this dashboard using an 8-point spacing system, a unified design token set, one primary button style, WCAG AA contrast, and a clear typography hierarchy. Preserve all business logic.

One-click copy, designed to be pasted directly into Claude Code.

### Module 10 — CSS Generator ✅ DONE

Generates CSS variables, theme tokens, card/button/table/form styles, typography scale, spacing scale, and dark/light mode variants.

### Module 11 — HTML Improvements ✅ DONE

Generates better semantic HTML, ARIA attributes, accessibility fixes, and responsive layout adjustments.

### Module 12 — Design Token Generator ✅ DONE

Generates colors, spacing scale, radius scale, elevation/shadow scale, typography scale, animation/transition tokens.

### Module 13 — Accessibility Review ✅ DONE

Analyzes WCAG conformance, keyboard navigation, contrast ratios, ARIA usage, alt text, focus order, and touch target sizing.

### Module 14 — Dashboard Analyzer ✅ DONE

Special-cased rules for dashboards: too many cards, poor hierarchy, crowded layouts, weak KPI presentation, bad charts, overly dense tables.

### Module 15 — Mobile Analyzer ✅ DONE

Scores responsive layout, overflow handling, touch target size, mobile navigation patterns, spacing, and font sizing.

### Module 16 — Consistency Checker ✅ DONE

Compares pages within a project (Page A vs. B vs. C) and flags divergent buttons, fonts, spacing, headers, and cards.

### Module 17 — UI Trend Analysis ✅ DONE

Every review is stored, enabling a score-over-time view per project (e.g., Jan 72 → Feb 80 → Mar 84 → Apr 91).

### Module 18 — Achievements (Gamification) ✅ DONE

Badges such as Typography Master, Dashboard Expert, Accessibility Champion, 90+ Club, Design System Complete. Encourages return visits and steady improvement rather than a single one-off scan.

### Module 19 — Inspiration Gallery

Browsable categories (Finance Dashboards, CRM, Analytics, AI Apps, Forms, Tables, Admin Panels, Developer Portals, Modern SaaS), each example annotated with *why it works*.

### Module 20 — Component Library

Automatically extracts buttons, cards, dialogs, tables, and forms from analyzed pages into a reusable design system for the project.

### Module 21 — Before/After Preview ✅ DONE

Visual side-by-side: current score vs. projected score after applying recommended fixes, broken down by category delta.

### Module 22 — Developer Dashboard (Home Page) ✅ DONE

The product's front door. Not an upload form — a workspace. Shows: overall UI score, project list with individual scores, recent reviews, current goal (e.g., "reach 90+"), recent improvements, today's recommendations, quick-analyze entry points, learning progress, and achievements. Feels like GitHub meets Linear, not a file-upload utility.

---

## UI COMPONENTS ANALYZED

Cards, Tables, Buttons, Forms, Navigation, Charts, Badges, Progress Bars, Empty States, Dialogs, Modals, Sidebars, Headers, Footers.

## SEVERITY LEVELS

Critical, High, Medium, Low, Suggestion.

## DESIGN RULES ENGINE

Rules are **data, not code** — defined in YAML, executed by analyzers, rather than hard-coded per-analyzer logic. This extends the existing coding standard ("favor configuration-driven rules... in configuration files rather than hard-coded") into the rule layer itself, not just scoring weights.

```
backend/
├── analyzers/        # read input (screenshot/HTML/CSS), execute applicable rules
└── rules/
    ├── spacing.yml
    ├── typography.yml
    ├── contrast.yml
    ├── tables.yml
    ├── buttons.yml
    ├── forms.yml
    ├── charts.yml
    └── dashboard.yml
```

**Why YAML rules instead of one Python file per rule type:**

- **Input-agnostic evaluation** — the same rule (e.g. "button padding should be at least 12px") can be evaluated regardless of whether the input came from a screenshot, HTML, or CSS, since the rule itself just describes a threshold/condition, not a parsing routine. Analyzers handle input-specific parsing; rules stay declarative.
- **Easier to maintain and test** — changing a threshold is a config edit, not a code change and redeploy.
- **Easier to extend** — new UI patterns or framework-specific conventions can be added as new YAML entries without touching analyzer code.
- **Cleaner tests** — tests validate business rules (does a 10px-padded button get flagged?) rather than parser implementation details.

Each rule entry returns: Issue, Severity, Confidence, and a Fix Recommendation — matching the existing Module 6 issue-detection contract.

## REPORT FORMAT

```
UI SCORE: 84/100

Top Issues
Top Improvements
Quick Wins
Accessibility
Consistency
Spacing
Typography
Color Usage
Component Review
Summary
```

---

## CODING STANDARDS

- Keep business logic out of API endpoints.
- Each analyzer has a single responsibility.
- No duplicate rules across analyzers.
- Structured logging instead of silent exception handling — no bare `except: pass`.
- Every public service has unit tests.
- Configuration-driven rules: scoring weights and thresholds (typography, contrast, spacing) live in config files, not hard-coded constants.
- Dependency injection where it reduces coupling between services and repositories.
- Type hints throughout; static analysis via Ruff/MyPy.

---

## NON-FUNCTIONAL REQUIREMENTS

### Architecture
- Layered architecture (API → Services → Analyzers → Rules → Repositories).
- No UI logic inside analyzers.
- No duplicated rules.

### Code Quality
- 90%+ unit test coverage for analysis and scoring engines.
- Structured logging; no silent exception swallowing.
- Type hints throughout.
- Static analysis (Ruff/MyPy) run in CI.

### Performance
- Screenshot analysis under 5 seconds for a typical dashboard.
- Rule evaluation under 1 second after analysis completes.
- Report generation under 2 seconds.
- Repeat analyses cached where possible.

### Security
- Uploaded screenshots are not retained beyond the configured retention window unless the user explicitly saves them to a project.
- HTML uploads are sanitized before parsing.
- Secrets are stripped from uploaded code where feasible.
- Any stored API keys are encrypted at rest.

### Documentation
- Architecture Decision Records (ADRs) for major design choices.
- OpenAPI documentation for the API.
- Developer guide and contribution guide.
- Rule-authoring guide so new analyzers/rules can be added consistently.

---

## TESTING REQUIREMENTS

Deterministic unit tests required for:

- Screenshot Analyzer
- Rule Engine
- Score Calculator
- Accessibility Checks
- Contrast Validation
- Typography Rules
- Spacing Rules
- Report Generator

Every analyzer must be deterministic and unit-testable in isolation — no test should depend on a live model call producing the same output twice.

---

## SUCCESS CRITERIA (VERSION 1)

A user can:

1. Create a project.
2. Upload screenshots or HTML/CSS.
3. Receive a detailed UI score with category breakdown.
4. See prioritized issues with estimated impact and estimated time-to-fix.
5. Learn *why* each issue matters, with reference examples (Stripe/Linear/Notion-style).
6. Generate CSS and a Claude prompt to fix issues.
7. Compare UI quality over time across reviews.
8. Track progress toward a target score.
9. Build a consistent design system across multiple pages within a project.

---

## DEFINITION OF DONE — SPEC 1

- ✅ Public GitHub repository created.
- ✅ Project structure committed.
- ✅ Development environment runs locally.
- ✅ FastAPI application starts successfully.
- ✅ Basic frontend displays the Developer Dashboard (Module 22), not a placeholder upload form.
- ✅ CI runs linting and tests on every pull request.
- ✅ README includes vision, architecture, roadmap, and setup instructions.
- ✅ Initial scoring model documented.
- ✅ First sample screenshot included for future testing.

---

## FUTURE VERSIONS

### Version 2 — GitHub Integration
Analyze pull requests, compare commits, detect UI regressions before merge.

### Version 3 — Browser Extension
Analyze live websites directly, no screenshot upload required.

### Version 4 — Figma Plugin
Bring scoring and recommendations into the design tool itself.

### Version 5 — VS Code Extension
Live feedback while coding, before a build is even run.

### Version 6 — CI/CD Integration
Fail a build if accessibility decreases, consistency decreases, or contrast violations increase versus the previous baseline.

---

## CHANGE LOG (this document)

- **v1.3.0** — Converged Claude/ChatGPT recommendations: renamed Module 3b to "Benchmark Library" (from "Reference Dataset"), reduced launch target to ~120 images, added HTML+CSS+component-tree+design-token comparison alongside screenshot similarity, marked Module 3b as an optional Phase-4 enhancement rather than a dependency. Added explicit 7-phase Build Order. Converted the Rule Engine from per-type Python files to a YAML-based Design Rules Engine (rules as data, input-agnostic, executed by analyzers). Added score-increase chaining to Module 7. Explicitly deferred the community/user-feedback learning loop — named in spec but not architected or built, gated on Version 1.5 client access and a deliberate privacy/retention review.
- **v1.2.0** — Expanded Module 3b with the full reference-dataset design: image+JSON metadata pairing, excellent/poor dual dataset, 13-category structure, the similarity comparison-output feature, and explicit guidance to source real (not AI-generated) screenshots while keeping the dataset private/local rather than committed to the public repo.
- **v1.1.0** — Locked V1 to a single-operator usage model (no client logins, no concurrency). Added Module 3b (free local embedding-similarity scoring as a no-cost substitute for vision-LLM quality judgment) with concrete storage sizing. Deferred client-facing access to Version 1.5 in the roadmap, to be built only once concurrent client demand justifies the added auth/data-isolation complexity.
- **v1.0.0** — Initial living requirements document created, consolidating SPEC 1 (MVP scope) with the full platform vision (22 modules, gamification, prompt generator, design system detection) from the project discussion.
