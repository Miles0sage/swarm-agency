"""Decision templates — pre-built question formats for common business decisions."""

from dataclasses import dataclass, field
from typing import Optional

from .types import AgencyRequest


@dataclass
class DecisionTemplate:
    """A reusable template for common business decisions."""
    name: str
    question_format: str
    departments: list[str]
    required_fields: list[str]
    default_context: str = ""


TEMPLATES: dict[str, DecisionTemplate] = {
    "hire": DecisionTemplate(
        name="Hire Decision",
        question_format="Should we hire {candidate} for the {role} position?",
        departments=["Operations", "Finance", "Strategy"],
        required_fields=["candidate", "role"],
        default_context="Evaluate candidate fit, compensation impact, and strategic alignment.",
    ),
    "pricing": DecisionTemplate(
        name="Pricing Change",
        question_format="Should we change pricing for {product} from {current_price} to {new_price}?",
        departments=["Finance", "Sales", "Marketing", "Strategy"],
        required_fields=["product", "current_price", "new_price"],
        default_context="Analyze revenue impact, competitive positioning, and customer retention risk.",
    ),
    "launch": DecisionTemplate(
        name="Product Launch",
        question_format="Should we launch {product} to {market}?",
        departments=["Product", "Engineering", "Marketing", "Strategy"],
        required_fields=["product", "market"],
        default_context="Evaluate market readiness, technical readiness, and go-to-market strategy.",
    ),
    "vendor": DecisionTemplate(
        name="Vendor Selection",
        question_format="Should we select {vendor} as our {service} provider?",
        departments=["Operations", "Finance", "Engineering", "Legal"],
        required_fields=["vendor", "service"],
        default_context="Evaluate vendor reliability, cost, integration complexity, and contract terms.",
    ),
    "pivot": DecisionTemplate(
        name="Strategic Pivot",
        question_format="Should we pivot from {current_direction} to {new_direction}?",
        departments=["Strategy", "Finance", "Product", "Engineering"],
        required_fields=["current_direction", "new_direction"],
        default_context="Analyze market signals, resource requirements, and risk of both paths.",
    ),
}


def list_templates() -> list[str]:
    """Return available template names."""
    return list(TEMPLATES.keys())


def create_request(template_name: str, request_id: Optional[str] = None, context: Optional[str] = None, **kwargs) -> AgencyRequest:
    """Create an AgencyRequest from a template.

    Raises ValueError if template not found or required fields missing.
    """
    if template_name not in TEMPLATES:
        raise ValueError(
            f"Unknown template: {template_name}. "
            f"Available: {', '.join(TEMPLATES.keys())}"
        )

    template = TEMPLATES[template_name]

    missing = [f for f in template.required_fields if f not in kwargs]
    if missing:
        raise ValueError(
            f"Template '{template_name}' requires fields: {', '.join(missing)}"
        )

    question = template.question_format.format(**kwargs)
    final_context = context or template.default_context

    import uuid
    rid = request_id or f"tmpl-{uuid.uuid4().hex[:8]}"

    return AgencyRequest(
        request_id=rid,
        question=question,
        context=final_context,
        department=None,
        metadata={"template": template_name, "template_fields": kwargs},
    )
