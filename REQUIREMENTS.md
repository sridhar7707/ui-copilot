# UICopilot — Living Requirements Document

Auto-generated and auto-updated.
Last updated: 2026-06-26 15:45:00 UTC
Version: 1.1.0 (auto-incremented on every update)

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
│   ├── rules/
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

## PRODUCT MODULES

The platform is organized into 22 modules. V1 (see Success Criteria) implements a focused subset; the rest are designed now so later modules slot in without rearchitecting.

### Module 1 — Project Management

Users create projects (e.g. "TradeGenius," "Landlord Copilot," "My CRM"). Each project stores its pages, screenshots, reports, scores, and history.

### Module 2 — Page Analyzer

**Inputs:** Screenshot, URL, HTML, CSS, React, Streamlit, Gradio.

**Outputs:** Overall Score, Visual Score, Accessibility Score, Professional Score, Modern Design Score, Consistency Score, Developer Score, Maintainability Score.

### Module 3 — Screenshot Analysis

Detects: cards, tables, buttons, navigation, charts, typography, whitespace, colors, forms, icons, badges, progress bars, dialogs, modals, headers, footers.

Detection uses free, locally-run techniques rather than a paid vision-LLM API call:

- **Deterministic CV** (free) — OpenCV/Pillow-based layout detection, color extraction (k-means palette clustering), and spacing measurement between detected elements. Handles contrast, alignment, and palette-harmony checks with full accuracy since these are arithmetic, not judgment calls.
- **Open-source layout/component models** (free) — locally-run, CPU-friendly models (e.g. HuggingFace layout-detection models) for classifying cards/tables/buttons/nav from pixels. Narrower than a vision-LLM but accurate enough for the standard UI component vocabulary.
- **Framework fingerprinting** (free) — known CSS/visual signatures of Bootstrap, Tailwind, and Material defaults are matched against uploaded HTML/CSS (or inferred from screenshot color/shape patterns when no source is available) to flag "looks like an unstyled default."

### Module 3b — Reference-Similarity Scoring

Approximates the "does this look professional" judgment a vision-LLM would make, without calling one.

**Approach:** a curated local reference set of known-good UI screenshots (Stripe-, Linear-, Notion-style examples, organized by component category — cards, tables, dashboards, forms, nav) is embedded once using a free, locally-run embedding model (e.g. an open-source CLIP variant). Each new analysis embeds the uploaded screenshot the same way and scores it by similarity-to-reference rather than by asking a model to judge quality from scratch — converting a subjective judgment into a free distance calculation.

**Sizing:**

- Reference set: ~50 categories × ~20 images = ~1,000 reference images.
- Raw reference images: ~1GB (not needed at runtime — only used once, during precompute).
- Stored embeddings (the only thing needed at runtime): ~3KB per image → **~3MB total**. Negligible footprint.
- Per-user analysis data (screenshots, HTML/CSS, reports, history) is the actual long-term storage driver and scales with usage, not with this feature — this is why uploaded screenshots are not retained beyond the configured window unless explicitly saved to a project (see Security, below).

**Resource requirement:** the embedding model must be loaded once at process startup and kept resident in memory — never reloaded per-request. Under the single-operator usage model (see Step 4), this is a correctness/efficiency best practice rather than a hard requirement, since there is no concurrent load to cause memory pressure; it becomes load-bearing if/when Version 1.5 (Client Access, see `ROADMAP.md`) introduces concurrent usage.

### Module 4 — Design System Detection

Automatically discovers buttons, cards, inputs, tables, badges, dialogs, colors, spacing, and typography in use, then flags inconsistency.

Example: *Buttons — 6 primary styles detected ❌ → Recommendation: reduce to one.*

### Module 5 — Scoring Engine

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

### Module 6 — Issue Detection

Every issue carries: Severity, Confidence, Evidence, Screenshot Highlight, Recommendation, Estimated Improvement, Estimated Time.

```
Issue: Button Padding
Severity: High
Estimated Gain: +4
Time: 2 minutes
```

### Module 7 — Improvement Roadmap

Generates Top 10 Improvements, Quick Wins, High Impact items, Easy Fixes, Accessibility Fixes, Visual Improvements, and Consistency Improvements — ranked, not just listed.

### Module 8 — Learning Mode

Every recommendation teaches, rather than just states the problem:

```
Problem: Typography hierarchy
Why: Users scan before reading.
Fix: Increase hero metrics to 32px.
Examples: Stripe, Linear, Notion
```

### Module 9 — Claude Prompt Generator

Generates a ready-to-paste prompt summarizing the fixes needed, e.g.:

> Refactor this dashboard using an 8-point spacing system, a unified design token set, one primary button style, WCAG AA contrast, and a clear typography hierarchy. Preserve all business logic.

One-click copy, designed to be pasted directly into Claude Code.

### Module 10 — CSS Generator

Generates CSS variables, theme tokens, card/button/table/form styles, typography scale, spacing scale, and dark/light mode variants.

### Module 11 — HTML Improvements

Generates better semantic HTML, ARIA attributes, accessibility fixes, and responsive layout adjustments.

### Module 12 — Design Token Generator

Generates colors, spacing scale, radius scale, elevation/shadow scale, typography scale, animation/transition tokens.

### Module 13 — Accessibility Review

Analyzes WCAG conformance, keyboard navigation, contrast ratios, ARIA usage, alt text, focus order, and touch target sizing.

### Module 14 — Dashboard Analyzer

Special-cased rules for dashboards: too many cards, poor hierarchy, crowded layouts, weak KPI presentation, bad charts, overly dense tables.

### Module 15 — Mobile Analyzer

Scores responsive layout, overflow handling, touch target size, mobile navigation patterns, spacing, and font sizing.

### Module 16 — Consistency Checker

Compares pages within a project (Page A vs. B vs. C) and flags divergent buttons, fonts, spacing, headers, and cards.

### Module 17 — UI Trend Analysis

Every review is stored, enabling a score-over-time view per project (e.g., Jan 72 → Feb 80 → Mar 84 → Apr 91).

### Module 18 — Achievements (Gamification)

Badges such as Typography Master, Dashboard Expert, Accessibility Champion, 90+ Club, Design System Complete. Encourages return visits and steady improvement rather than a single one-off scan.

### Module 19 — Inspiration Gallery

Browsable categories (Finance Dashboards, CRM, Analytics, AI Apps, Forms, Tables, Admin Panels, Developer Portals, Modern SaaS), each example annotated with *why it works*.

### Module 20 — Component Library

Automatically extracts buttons, cards, dialogs, tables, and forms from analyzed pages into a reusable design system for the project.

### Module 21 — Before/After Preview

Visual side-by-side: current score vs. projected score after applying recommended fixes, broken down by category delta.

### Module 22 — Developer Dashboard (Home Page)

The product's front door. Not an upload form — a workspace. Shows: overall UI score, project list with individual scores, recent reviews, current goal (e.g., "reach 90+"), recent improvements, today's recommendations, quick-analyze entry points, learning progress, and achievements. Feels like GitHub meets Linear, not a file-upload utility.

---

## UI COMPONENTS ANALYZED

Cards, Tables, Buttons, Forms, Navigation, Charts, Badges, Progress Bars, Empty States, Dialogs, Modals, Sidebars, Headers, Footers.

## SEVERITY LEVELS

Critical, High, Medium, Low, Suggestion.

## RULE ENGINE

`backend/rules/` — one file per concern, each rule returns Issue, Severity, Confidence, and a Fix Recommendation:

- `spacing_rules.py`
- `typography_rules.py`
- `contrast_rules.py`
- `table_rules.py`
- `button_rules.py`
- `form_rules.py`
- `chart_rules.py`
- `dashboard_rules.py`

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

- **v1.1.0** — Locked V1 to a single-operator usage model (no client logins, no concurrency). Added Module 3b (free local embedding-similarity scoring as a no-cost substitute for vision-LLM quality judgment) with concrete storage sizing. Deferred client-facing access to Version 1.5 in the roadmap, to be built only once concurrent client demand justifies the added auth/data-isolation complexity.
- **v1.0.0** — Initial living requirements document created, consolidating SPEC 1 (MVP scope) with the full platform vision (22 modules, gamification, prompt generator, design system detection) from the project discussion.
