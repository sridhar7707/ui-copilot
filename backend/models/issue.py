from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SUGGESTION = "suggestion"


class Category(str, Enum):
    VISUAL_HIERARCHY = "visual_hierarchy"
    TYPOGRAPHY = "typography"
    SPACING = "spacing"
    CONSISTENCY = "consistency"
    ACCESSIBILITY = "accessibility"
    CONTRAST = "contrast"
    COMPONENT_QUALITY = "component_quality"
    CONVERSION_OPTIMIZATION = "conversion_optimization"
    UX_QUALITY = "ux_quality"
    PERFORMANCE = "performance"
    INTERACTIVITY = "interactivity"


@dataclass
class Issue:
    rule_id: str
    category: Category
    severity: Severity
    confidence: float  # 0.0–1.0
    message: str
    recommendation: str
    evidence: str
    estimated_time: str  # human-readable, e.g. "5 minutes"
    estimated_gain: float = field(default=0.0)  # overall score points; set by scoring engine
    why: str = ""  # why this issue matters to users (Learning Mode)
    references: list[str] = field(default_factory=list)  # products/specs that do it right
