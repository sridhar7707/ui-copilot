# UICopilot Roadmap

## Version 1 — Foundation (current)

Screenshot, HTML, and CSS analysis only.

- Project management (create/store projects, pages, screenshots, reports)
- Screenshot Analyzer, HTML Analyzer, CSS Analyzer
- Scoring Engine (7 weighted categories, 0–100 scale)
- Rule Engine (`spacing_rules.py`, `typography_rules.py`, `contrast_rules.py`, `table_rules.py`, `button_rules.py`, `form_rules.py`, `chart_rules.py`, `dashboard_rules.py`)
- Issue Detection with severity, confidence, estimated gain, estimated time
- Improvement Roadmap (Top 10, Quick Wins, High Impact, Easy Fixes)
- Learning Mode (why each issue matters + reference examples)
- Claude Prompt Generator (one-click copy, paste straight into Claude Code)
- Design System Detection (flag inconsistent buttons/cards/tables)
- Trend tracking across reviews
- Developer Dashboard home page (Module 22)

**Explicitly excluded from V1:** AI chat, Figma plugin, live browser extension, full auto code generation, multi-user accounts, cloud deployment.

**Usage model for V1:** Single-operator. You (and your team) run analyses and relay findings to clients as commentary — clients do not log into the tool directly. This removes the need for authentication, multi-tenant data isolation, and concurrent-request handling, and keeps the free-tier compute (HuggingFace Spaces CPU-basic) comfortable, since only one analysis runs at a time.

---

## Version 1.5 — Client Access (deferred until needed)

Triggered when there are enough concurrent clients that relaying findings manually becomes the bottleneck — not built speculatively.

Reopens scope that V1 deliberately excludes:

- **Accounts & authentication** — clients log in and see only their own projects (login flow, session/JWT handling, per-query data scoping)
- **Multi-tenant data isolation** — strict separation so Client A never sees Client B's screenshots, scores, or reports
- **Concurrency handling** — the embedding model and analysis pipeline need to safely serve simultaneous requests rather than the current one-at-a-time assumption; likely point where free CPU tiers stop being sufficient and a paid compute tier becomes worth it
- **Permissions model** — decide what clients see vs. what stays internal-only (e.g. raw module breakdowns vs. a curated client-facing report)
- **Client-facing UX hardening** — error states, empty states, and loading states need to be production-grade rather than internal-tool-rough

This is intentionally scoped as its own phase rather than folded into V1, since authentication and data isolation are security-sensitive and deserve focused attention rather than being bolted on alongside other feature work.

---

## Version 2 — GitHub Integration

- Analyze pull requests directly
- Compare commits to detect UI regressions before merge
- Comment on PRs with score deltas and flagged issues

## Version 3 — Browser Extension

- Analyze live websites without a manual screenshot upload
- Inspect a running app in the same way as an uploaded screenshot

## Version 4 — Figma Plugin

- Bring scoring and recommendations into the design tool, ahead of implementation

## Version 5 — VS Code Extension

- Live feedback while coding, before a build is even run
- Inline warnings tied to the same rule engine used by the web platform

## Version 6 — CI/CD Integration

- Fail a build if:
  - Accessibility score decreases
  - Consistency score decreases
  - Contrast violations increase
- Designed to act as a quality gate alongside existing linting/test CI steps

---

## Longer-Term Direction

```
UI Review → UX Review → Accessibility → Design System → Generate Fixes
   → Generate Code → Track Quality → CI Integration → Enterprise Dashboard
```

The throughline across every version: don't just report a problem — explain it, quantify its impact, and generate the fix. That's the same principle TradeGenius applies to trading recommendations, applied here to UI quality.
