from __future__ import annotations

from backend.models.issue import Category, Issue, Severity


def analyze(parsed_page: dict, thresholds: dict) -> list[Issue]:
    issues: list[Issue] = []
    t = thresholds["tables"]
    tables = parsed_page.get("tables", [])

    for i, table in enumerate(tables):
        label = f"Table #{i + 1}"

        # TBL1 — no header row
        if not table.get("has_header", True):
            issues.append(Issue(
                rule_id="TBL1_missing_header",
                category=Category.COMPONENT_QUALITY,
                severity=Severity.HIGH,
                confidence=0.95,
                message=f"{label} has no header row (<thead>/<th>).",
                recommendation=(
                    "Add a <thead> with <th> elements. Use scope='col' for accessibility. "
                    "Style headers to visually distinguish them from data rows."
                ),
                evidence="No <th> or <thead> detected.",
                estimated_time="10 minutes",
            ))

        # TBL2 — no zebra striping
        if not table.get("has_zebra_striping", False):
            issues.append(Issue(
                rule_id="TBL2_no_zebra",
                category=Category.COMPONENT_QUALITY,
                severity=Severity.LOW,
                confidence=0.7,
                message=f"{label} has no alternating row colours — dense tables are hard to scan.",
                recommendation="Apply a subtle background to odd/even rows (e.g. tr:nth-child(even) { background: #f9f9f9; }).",
                evidence="No alternating row background detected.",
                estimated_time="10 minutes",
            ))

        # TBL3 — insufficient cell padding
        cell_pad = table.get("cell_padding_px", 0)
        if cell_pad < t["min_cell_padding_px"]:
            issues.append(Issue(
                rule_id="TBL3_cell_padding",
                category=Category.COMPONENT_QUALITY,
                severity=Severity.MEDIUM,
                confidence=0.9,
                message=(
                    f"{label} cell padding ({cell_pad}px) is below the "
                    f"recommended {t['min_cell_padding_px']}px."
                ),
                recommendation=f"Set td, th {{ padding: {t['min_cell_padding_px']}px 12px; }} for comfortable reading.",
                evidence=f"td padding: {cell_pad}px",
                estimated_time="5 minutes",
            ))

    return issues
