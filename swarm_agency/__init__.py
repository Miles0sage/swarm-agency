"""swarm-agency: 43 AI personas across 10 departments. Multi-model debate engine."""

from .types import AgentConfig, AgencyRequest, AgentVote, Decision
from .department import Department
from .agency import Agency
from .learning import LearningEngine, Feedback
from .presets import (
    ALL_AGENTS,
    DEPARTMENT_NAMES,
    create_strategy_dept,
    create_product_dept,
    create_marketing_dept,
    create_research_dept,
    create_finance_dept,
    create_engineering_dept,
    create_legal_dept,
    create_operations_dept,
    create_sales_dept,
    create_creative_dept,
    create_full_agency_departments,
)

__version__ = "0.2.0"
__all__ = [
    "Agency",
    "AgencyRequest",
    "AgentConfig",
    "AgentVote",
    "ALL_AGENTS",
    "Decision",
    "Department",
    "DEPARTMENT_NAMES",
    "Feedback",
    "LearningEngine",
    "create_creative_dept",
    "create_engineering_dept",
    "create_finance_dept",
    "create_full_agency_departments",
    "create_legal_dept",
    "create_marketing_dept",
    "create_operations_dept",
    "create_product_dept",
    "create_research_dept",
    "create_sales_dept",
    "create_strategy_dept",
]
