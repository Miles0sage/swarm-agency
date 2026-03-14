"""DSPy-based prompt optimization for swarm-agency agents.

Optimizes a single AgentVoter module that generalizes across all 43 personas.
Role, expertise, and bias are INPUT fields — MIPROv2 optimizes the shared
instruction template and few-shot demos, then it works for all agents.

Requires: pip install dspy-ai
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .types import AgentConfig
from .memory import DecisionMemoryStore

logger = logging.getLogger("swarm_agency.dspy_optimizer")

OPTIMIZED_DIR = Path("~/.swarm-agency/dspy_optimized").expanduser()


def _check_dspy():
    """Check if dspy-ai is installed."""
    try:
        import dspy
        return True
    except ImportError:
        return False


def build_trainset_from_memory(
    memory_store: DecisionMemoryStore,
    agent_configs: Optional[dict[str, AgentConfig]] = None,
) -> list[dict]:
    """Export feedback-labeled decisions as training data for DSPy.

    Returns list of dicts with: question, context, role, expertise, bias,
    position (ground truth), feedback_correct.
    """
    history = memory_store.get_history(limit=500)
    records = []

    for record in history:
        if record.feedback_correct is None:
            continue

        # The correct position is the decision position if feedback says correct
        if record.feedback_correct:
            correct_pos = record.position
        else:
            continue  # Skip incorrect decisions without a known correct answer

        if record.votes_json:
            votes = json.loads(record.votes_json)
            for vote in votes:
                agent_name = vote.get("agent_name", "")
                cfg = agent_configs.get(agent_name) if agent_configs else None

                records.append({
                    "question": record.question,
                    "context": record.context or "",
                    "role": cfg.role if cfg else vote.get("role", "Analyst"),
                    "expertise": cfg.expertise if cfg else vote.get("expertise", "general analysis"),
                    "bias": cfg.bias if cfg else vote.get("bias", "balanced"),
                    "position": correct_pos,
                })

    return records


def optimize_prompts(
    memory_store: DecisionMemoryStore,
    agent_configs: Optional[dict[str, AgentConfig]] = None,
    prompt_model: str = "openai/gpt-4o-mini",
    task_model: str = "openai/qwen3-coder-plus",
    api_key: str = "",
    base_url: str = "",
    auto: str = "light",
    save_dir: Optional[str] = None,
) -> dict:
    """Run DSPy MIPROv2 optimization on agent voting prompts.

    Requires dspy-ai installed and at least 20 feedback records.
    Returns dict with optimized instruction and stats.
    """
    if not _check_dspy():
        return {
            "status": "error",
            "message": "dspy-ai not installed. Run: pip install dspy-ai",
        }

    import dspy

    trainset_raw = build_trainset_from_memory(memory_store, agent_configs)
    if len(trainset_raw) < 20:
        return {
            "status": "error",
            "message": f"Need at least 20 feedback records, got {len(trainset_raw)}",
        }

    # Define DSPy signature and module
    class AgentVoteSignature(dspy.Signature):
        """You are a business advisor voting on a strategic decision.
        Analyze from your specific role, expertise, and analytical bias.
        Vote YES, NO, or MAYBE with confidence and reasoning."""

        question: str = dspy.InputField(desc="Business question to decide")
        context: str = dspy.InputField(desc="Additional context")
        role: str = dspy.InputField(desc="Your organizational role")
        expertise: str = dspy.InputField(desc="Your domain expertise")
        bias: str = dspy.InputField(desc="Your analytical perspective")
        position: str = dspy.OutputField(desc="YES, NO, or MAYBE")
        confidence: float = dspy.OutputField(desc="0.0-1.0")
        reasoning: str = dspy.OutputField(desc="2-3 sentence explanation")

    class AgentVoterModule(dspy.Module):
        def __init__(self):
            super().__init__()
            self.vote = dspy.Predict(AgentVoteSignature)

        def forward(self, question, context, role, expertise, bias):
            return self.vote(
                question=question, context=context,
                role=role, expertise=expertise, bias=bias,
            )

    def voting_metric(example, prediction, trace=None) -> float:
        pred = getattr(prediction, "position", "").upper().strip()
        gold = example.position.upper().strip()
        if pred == gold:
            return 1.0
        if pred == "MAYBE":
            return 0.3
        return 0.0

    # Build DSPy examples
    examples = []
    for rec in trainset_raw:
        ex = dspy.Example(
            question=rec["question"],
            context=rec["context"],
            role=rec["role"],
            expertise=rec["expertise"],
            bias=rec["bias"],
            position=rec["position"],
        ).with_inputs("question", "context", "role", "expertise", "bias")
        examples.append(ex)

    # Configure LMs
    prompt_lm = dspy.LM(prompt_model, api_key=api_key, api_base=base_url)
    task_lm = dspy.LM(task_model, api_key=api_key, api_base=base_url)
    dspy.configure(lm=task_lm)

    # Run optimization
    out_dir = Path(save_dir) if save_dir else OPTIMIZED_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    student = AgentVoterModule()
    optimizer = dspy.MIPROv2(
        metric=voting_metric,
        prompt_model=prompt_lm,
        task_model=task_lm,
        auto=auto,
        max_bootstrapped_demos=3,
        max_labeled_demos=3,
        verbose=True,
        log_dir=str(out_dir / "logs"),
    )

    optimized = optimizer.compile(
        student=student,
        trainset=examples,
        minibatch_size=min(25, len(examples)),
    )

    # Save
    save_path = out_dir / "optimized_voter.json"
    optimized.save(str(save_path))

    # Extract optimized instruction
    instruction = None
    for _, predictor in optimized.named_predictors():
        instruction = predictor.signature.instructions
        break

    return {
        "status": "success",
        "training_examples": len(examples),
        "optimized_instruction": instruction,
        "saved_to": str(save_path),
    }


def load_optimized_instruction(save_dir: Optional[str] = None) -> Optional[str]:
    """Load the optimized instruction from a previous optimization run."""
    out_dir = Path(save_dir) if save_dir else OPTIMIZED_DIR
    save_path = out_dir / "optimized_voter.json"

    if not save_path.exists():
        return None

    if not _check_dspy():
        # Try to read raw JSON
        try:
            data = json.loads(save_path.read_text())
            # DSPy saves in a specific format, try to extract instruction
            for key, val in data.items():
                if isinstance(val, dict) and "signature" in str(val):
                    return val.get("signature", {}).get("instructions")
        except (json.JSONDecodeError, OSError):
            pass
        return None

    import dspy

    class AgentVoteSignature(dspy.Signature):
        """Placeholder."""
        question: str = dspy.InputField()
        context: str = dspy.InputField()
        role: str = dspy.InputField()
        expertise: str = dspy.InputField()
        bias: str = dspy.InputField()
        position: str = dspy.OutputField()
        confidence: float = dspy.OutputField()
        reasoning: str = dspy.OutputField()

    class AgentVoterModule(dspy.Module):
        def __init__(self):
            super().__init__()
            self.vote = dspy.Predict(AgentVoteSignature)

    module = AgentVoterModule()
    module.load(str(save_path))

    for _, predictor in module.named_predictors():
        return predictor.signature.instructions
    return None


def apply_optimized_to_agent(
    agent: AgentConfig,
    optimized_instruction: str,
) -> AgentConfig:
    """Create a new AgentConfig with the DSPy-optimized instruction."""
    return AgentConfig(
        name=agent.name,
        role=agent.role,
        expertise=agent.expertise,
        bias=agent.bias,
        system_prompt=optimized_instruction,
        model=agent.model,
    )
