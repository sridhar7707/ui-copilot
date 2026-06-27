# UICopilot

**AI UI/UX Engineering Platform** — analyze, score, and improve the visual quality of your application.

UICopilot reviews screenshots, HTML, and CSS, scores interface quality across the dimensions that actually make software look professional, and turns every issue it finds into a prioritized, explainable fix — not just a grade.

> Built for developers who say *"I can build software, but I can't make it look good."*

---

## Why UICopilot

Most UI checkers stop at "here's your score." UICopilot is built on a different premise: **the score is not the product — the prioritized action plan is.**

```
UI Score: 82/100

Increase card padding from 12px to 20px       (+4 points)
Make table headers 13px uppercase             (+3 points)
Standardize primary button styling            (+2 points)
```

Every issue UICopilot surfaces includes the problem, the evidence, why it matters, the recommended fix, and the expected score impact. No vague suggestions.

## What It Does

- **Scores your UI** across visual hierarchy, typography, spacing, consistency, accessibility, contrast, and component quality.
- **Detects issues** with severity, confidence, and an estimated point gain for fixing each one.
- **Finds inconsistency** — e.g. six different button styles where there should be one — and tells you how to consolidate.
- **Teaches as it goes**: every recommendation explains *why* it matters, with reference points from products like Stripe, Linear, and Notion.
- **Generates fixes**: CSS variables, design tokens, semantic HTML/ARIA improvements, and a ready-to-paste prompt for Claude Code.
- **Tracks progress over time**, so you can see whether today's changes actually improved your UI.

## Architecture

```
Frontend
   ↓
FastAPI Backend
   ↓
Analysis Engine
   ├── Screenshot Analyzer        ├── Color Analyzer
   ├── HTML Analyzer              ├── Dashboard Analyzer
   ├── CSS Analyzer               ├── Table Analyzer
   ├── Component Analyzer         ├── Mobile Analyzer
   ├── Accessibility Analyzer     └── Design System Analyzer
   ├── Typography Analyzer
   └── Spacing Analyzer
   ↓
Recommendation Engine → Score Engine → Learning Engine → Claude Prompt Generator
   ↓
SQLite (DuckDB planned for analytics & trend history)
```

Layered design throughout: API → Services → Analyzers → Rules → Repositories. Analyzers have no UI logic and no direct database access; scoring weights and thresholds are configuration-driven, not hard-coded.

## Project Structure

```
ui-copilot/
├── backend/
│   ├── api/            # FastAPI routes — no business logic here
│   ├── services/        # Orchestration layer
│   ├── analyzers/       # Screenshot / HTML / CSS / component analyzers
│   ├── rules/           # spacing_rules.py, typography_rules.py, contrast_rules.py, ...
│   ├── models/
│   ├── repositories/
│   └── utils/
├── frontend/
│   ├── components/
│   ├── pages/
│   └── assets/
├── tests/
├── docs/                # REQUIREMENTS.md, specs/, ADRs
├── samples/
├── reports/
├── data/
├── config/               # scoring weights, thresholds — not in code
├── scripts/
└── requirements.txt
```

## Getting Started

```bash
# Clone
git clone https://github.com/<your-org>/ui-copilot.git
cd ui-copilot

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies (Python 3.9+)
pip install -r requirements.txt

# Start the server
uvicorn backend.api.main:app --reload
```

Then open **http://localhost:8000** — the Developer Dashboard loads automatically.

The API docs are at **http://localhost:8000/docs** (Swagger UI).

### Running tests

```bash
python -m pytest tests/ -v
```

### Linting

```bash
ruff check backend/ tests/
```

## V1 Modules — Status

| Module | Description | Status |
|--------|-------------|--------|
| 1  | Project Management (SQLite + CRUD) | ✅ Done |
| 2  | Page Analyzer (HTML + CSS parser) | ✅ Done |
| 3  | Screenshot Analysis (CV, no API calls) | ✅ Done |
| 4  | Design System Detection (6 rules) | ✅ Done |
| 5  | Scoring Engine (7 categories, config-driven) | ✅ Done |
| 6  | Issue Detection (severity, confidence, evidence) | ✅ Done |
| 7  | Improvement Roadmap (7 buckets) | ✅ Done |
| 8  | Learning Mode (why + references on every issue) | ✅ Done |
| 9  | Claude Prompt Generator | ✅ Done |
| 10 | CSS Generator | ✅ Done |
| 11 | HTML Improvements (ARIA, semantic, responsive) | ✅ Done |
| 12 | Design Token Generator (colors, spacing, elevation, animation, dark mode) | ✅ Done |
| 13 | Accessibility Review (WCAG A/AA, keyboard/ARIA hints) | ✅ Done |
| 14 | Dashboard Analyzer | ✅ Done |
| 15 | Mobile Analyzer | ✅ Done |
| 16 | Consistency Checker (cross-page divergence) | ✅ Done |
| 17 | UI Trend Analysis (score over time) | ✅ Done |
| 18 | Achievements / Gamification (14 badges) | ✅ Done |
| 22 | Developer Dashboard (workspace UI at `/`) | ✅ Done |

## API Endpoints

```
POST /api/v1/analyze              — analyze HTML (+ optional CSS)
POST /api/v1/analyze/screenshot   — analyze a screenshot

GET  /api/v1/projects             — list projects
POST /api/v1/projects             — create project
GET  /api/v1/projects/{id}        — get project
DELETE /api/v1/projects/{id}      — delete project
GET  /api/v1/projects/{id}/pages  — list pages
POST /api/v1/projects/{id}/pages  — add page
GET  /api/v1/projects/{id}/trend        — score-over-time (all pages)
GET  /api/v1/projects/{id}/consistency  — cross-page consistency report
GET  /api/v1/projects/{id}/achievements — badges & gamification

GET  /api/v1/pages/{id}           — get page
GET  /api/v1/pages/{id}/analyses  — list analyses
GET  /api/v1/pages/{id}/trend     — score-over-time (one page)

GET  /health                      — health check
GET  /docs                        — Swagger UI
```

## Roadmap

UICopilot Version 1 covers screenshot, HTML, and CSS analysis with scoring, issue detection, the improvement roadmap, learning mode, and the Claude prompt generator. See [`ROADMAP.md`](./ROADMAP.md) for the full path: GitHub PR integration → browser extension → Figma plugin → VS Code extension → CI/CD quality gates.

Full module breakdown and detailed scope live in [`docs/REQUIREMENTS.md`](./docs/REQUIREMENTS.md), the project's living requirements document.

## Scoring Model

| Category | Weight |
|---|---|
| Visual Hierarchy | 20% |
| Typography | 15% |
| Spacing | 15% |
| Consistency | 15% |
| Accessibility | 15% |
| Contrast | 10% |
| Component Quality | 10% |

Scores are 0–100, per page, with category-level breakdowns and a trend view across reviews over time.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). New analyzers and rules should follow the single-responsibility pattern already used in `backend/rules/` — each rule returns an issue, severity, confidence score, and fix recommendation, and reads its thresholds from `config/`, not from hard-coded values.

## License

MIT — see [`LICENSE`](./LICENSE).
