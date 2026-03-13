"""swarm-agency: Multi-model AI agency where agents debate like departments in a business."""

from .types import AgentConfig, AgencyRequest, AgentVote, Decision
from .department import Department
from .agency import Agency
from .learning import LearningEngine, Feedback
from .presets import (
    create_strategy_dept,
    create_product_dept,
    create_marketing_dept,
    create_research_dept,
    create_full_agency_departments,
)

__version__ = "0.1.0"
__all__ = [
    "Agency",
    "AgencyRequest",
    "AgentConfig",
    "AgentVote",
    "Decision",
    "Department",
    "Feedback",
    "LearningEngine",
    "create_full_agency_departments",
    "create_marketing_dept",
    "create_product_dept",
    "create_research_dept",
    "create_strategy_dept",
]
