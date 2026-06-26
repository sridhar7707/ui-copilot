from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from typing_extensions import TypedDict

from backend.models.issue import Category, Issue


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

@dataclass
class CategoryScore:
    category: Category
    score: float  # 0–100
    weight: float
    issues: list[Issue] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class AnalysisResult:
    overall_score: float
    category_scores: list[CategoryScore]
    issues: list[Issue]  # all issues, sorted by estimated_gain descending

    @property
    def top_issues(self) -> list[Issue]:
        return self.issues[:10]

    @property
    def quick_wins(self) -> list[Issue]:
        return [
            i for i in self.issues
            if i.estimated_gain >= 1.0 and "minute" in i.estimated_time
        ]

    @property
    def high_impact(self) -> list[Issue]:
        """Issues with the largest estimated score gain (top 5)."""
        return [i for i in self.issues if i.estimated_gain >= 2.0][:5]

    @property
    def easy_fixes(self) -> list[Issue]:
        """Issues that can be resolved in minutes (all severities)."""
        return [i for i in self.issues if "minute" in i.estimated_time]

    @property
    def accessibility_fixes(self) -> list[Issue]:
        """All accessibility-category issues, highest gain first."""
        return [i for i in self.issues if i.category == Category.ACCESSIBILITY]

    @property
    def visual_improvements(self) -> list[Issue]:
        """Visual hierarchy and typography issues."""
        visual_cats = {Category.VISUAL_HIERARCHY, Category.TYPOGRAPHY}
        return [i for i in self.issues if i.category in visual_cats]

    @property
    def consistency_improvements(self) -> list[Issue]:
        """Consistency and spacing issues."""
        return [i for i in self.issues if i.category == Category.CONSISTENCY]

    @property
    def roadmap(self) -> dict:
        """Structured roadmap grouping all issue buckets."""
        return {
            "top_issues": self.top_issues,
            "quick_wins": self.quick_wins,
            "high_impact": self.high_impact,
            "easy_fixes": self.easy_fixes,
            "accessibility_fixes": self.accessibility_fixes,
            "visual_improvements": self.visual_improvements,
            "consistency_improvements": self.consistency_improvements,
        }


# ---------------------------------------------------------------------------
# Input schema — the contract between parsers and the rule engine.
# Rules consume these shapes; parsers must produce them.
# ---------------------------------------------------------------------------

class HeadingData(TypedDict):
    level: int          # 1–6
    font_size_px: float
    text: str


class ButtonData(TypedDict):
    padding_top_px: float
    padding_right_px: float
    padding_bottom_px: float
    padding_left_px: float
    background_color: str   # hex, e.g. "#007bff"
    color: str              # hex, text colour
    border_radius_px: float
    has_focus_style: bool
    height_px: float        # for touch-target check
    text: str


class InputData(TypedDict):
    has_label: bool
    label_text: Optional[str]
    placeholder: Optional[str]
    padding_px: float
    has_focus_style: bool
    input_type: str         # "text", "email", "password", ...


class TableData(TypedDict):
    has_header: bool
    has_zebra_striping: bool
    cell_padding_px: float
    has_border: bool


class CardData(TypedDict):
    padding_top_px: float
    padding_right_px: float
    padding_bottom_px: float
    padding_left_px: float


class ColorPairData(TypedDict):
    foreground: str     # hex
    background: str     # hex
    font_size_px: float
    is_bold: bool
    context: str        # "body", "button", "heading", "link"


class ChartData(TypedDict):
    has_axis_labels: bool
    color_count: int
    colors: list[str]   # hex colours used in the chart


class ParsedPage(TypedDict):
    # Typography
    fonts: list[str]
    headings: list[HeadingData]
    body_font_size_px: Optional[float]
    line_height: Optional[float]        # unitless ratio, e.g. 1.5
    # Components
    buttons: list[ButtonData]
    inputs: list[InputData]
    tables: list[TableData]
    cards: list[CardData]
    charts: list[ChartData]
    # Colours
    text_color_pairs: list[ColorPairData]
    # Dashboard-level
    kpi_card_count: int
    whitespace_ratio: float             # 0.0–1.0 estimate
    # Spacing inventory
    spacing_values_px: list[float]      # all margin/padding values found
