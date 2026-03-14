"""swarm-agency: 43 AI personas across 10 departments. Multi-model debate engine."""

from .types import AgentConfig, AgencyRequest, AgentVote, Decision, DecisionRecord
from .department import Department
from .agency import Agency
from .learning import LearningEngine, Feedback
from .memory import DecisionMemoryStore, build_memory_context
from .embeddings import (
    get_embedding,
    get_embeddings_batch,
    cosine_similarity,
    embedding_to_bytes,
    bytes_to_embedding,
)
from .templates import (
    DecisionTemplate,
    TEMPLATES,
    create_request,
    list_templates,
)
from .streaming import VoteEvent, stream_debate, stream_department_debate
from .rounds import RoundResult, multi_round_debate
from .tools import ToolRegistry, ToolDefinition, ToolCall, ToolResult, default_registry
from .optimizer import PromptOptimizer, OptimizationResult
from .sports import create_sports_agency, create_sports_departments, ALL_SPORTS_AGENTS
from .web_search import web_search
from .soul import SoulStore, AgentSoul, Belief, Episode, format_soul_context
from .scheduler import AgentScheduler, ScheduledJob
from .alerts import Alert, decision_to_alert, format_alert_text
from .messaging import MessageBus, AgentMessage, auto_escalate
from .dual_debate import dual_debate, DualDebateResult
from .verdict import Verdict, decision_to_verdict, format_verdict_text
from .presets import (
    ALL_AGENTS,
    DEPARTMENT_NAMES,
    DEPARTMENT_DESCRIPTIONS,
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

__version__ = "1.0.0"
__all__ = [
    "Agency",
    "AgencyRequest",
    "AgentConfig",
    "AgentVote",
    "ALL_AGENTS",
    "build_memory_context",
    "bytes_to_embedding",
    "cosine_similarity",
    "create_request",
    "Decision",
    "DecisionMemoryStore",
    "DecisionRecord",
    "DecisionTemplate",
    "Department",
    "DEPARTMENT_DESCRIPTIONS",
    "DEPARTMENT_NAMES",
    "embedding_to_bytes",
    "Feedback",
    "get_embedding",
    "get_embeddings_batch",
    "LearningEngine",
    "list_templates",
    "TEMPLATES",
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
    "default_registry",
    "multi_round_debate",
    "RoundResult",
    "stream_debate",
    "stream_department_debate",
    "ToolCall",
    "ToolDefinition",
    "ToolRegistry",
    "ToolResult",
    "VoteEvent",
    "OptimizationResult",
    "PromptOptimizer",
    "ALL_SPORTS_AGENTS",
    "create_sports_agency",
    "create_sports_departments",
    "web_search",
    "AgentSoul",
    "Belief",
    "Episode",
    "format_soul_context",
    "SoulStore",
    "AgentScheduler",
    "ScheduledJob",
    "Alert",
    "decision_to_alert",
    "format_alert_text",
    "MessageBus",
    "AgentMessage",
    "auto_escalate",
    "dual_debate",
    "DualDebateResult",
    "Verdict",
    "decision_to_verdict",
    "format_verdict_text",
]
