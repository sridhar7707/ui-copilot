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

# Install dependencies
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the backend
uvicorn backend.api.main:app --reload

# Run the frontend
cd frontend && npm install && npm run dev
```

Upload a screenshot, HTML file, or CSS file from the dashboard to get your first score.

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
