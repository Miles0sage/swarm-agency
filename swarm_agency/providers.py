"""Multi-provider support for swarm-agency.

Supports DashScope (Alibaba) and OpenRouter (200+ models).
Each provider uses the OpenAI-compatible chat/completions API.
"""

PROVIDERS = {
    "dashscope": {
        "name": "DashScope (Alibaba)",
        "base_url": "https://coding-intl.dashscope.aliyuncs.com/v1",
        "env_key": "ALIBABA_CODING_API_KEY",
        "description": "$10/mo flat, 5 Chinese model families",
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "env_key": "OPENROUTER_API_KEY",
        "description": "Pay-per-use, 7 model families (Claude, GPT, Gemini, Llama, Mistral, DeepSeek, Qwen)",
    },
}

# ── OpenRouter Model Mapping ─────────────────────────────────────────
#
# Strategy: Assign each department models that match their expertise.
# Use 7 genuinely different providers for maximum reasoning diversity.
#
# Provider families:
#   1. Anthropic (Claude)  — Best reasoning, safety-aware
#   2. Google (Gemini)     — Broad knowledge, analytical
#   3. DeepSeek            — Strong reasoning, contrarian
#   4. Meta (Llama)        — Fast, direct, practical
#   5. Mistral             — European, precise, creative
#   6. Qwen (Alibaba)      — Technical, code-aware
#   7. OpenAI (GPT)        — Balanced, popular baseline

OPENROUTER_MODELS = {
    # ── Strategy Department ──
    # C-suite decisions need the best reasoners
    "Visionary":        "anthropic/claude-sonnet-4.6",      # Best reasoning for long-term strategy
    "Pragmatist":       "google/gemini-2.5-flash",          # Fast, practical analysis
    "NumbersCruncher":  "deepseek/deepseek-v3.2",           # Strong at quantitative reasoning
    "GrowthHacker":     "meta-llama/llama-4-maverick",      # Creative, unconventional thinking
    "DevilsAdvocate":   "mistralai/mistral-large-2512",     # European precision, contrarian

    # ── Product Department ──
    # Mix of user empathy and technical depth
    "UserAdvocate":     "anthropic/claude-haiku-4.5",       # Empathetic, user-focused
    "TechLead":         "deepseek/deepseek-v3.2",           # Deep technical reasoning
    "DesignThinker":    "mistralai/mistral-small-creative",  # Creative, design-oriented
    "DataDriven":       "google/gemini-2.5-pro",            # Analytical, data-focused
    "ShipIt":           "qwen/qwen3-coder-next",            # Fast, code-aware, ship-oriented

    # ── Marketing Department ──
    # Creative + analytical mix
    "BrandBuilder":     "anthropic/claude-sonnet-4.6",      # Nuanced brand strategy
    "ContentEngine":    "mistralai/mistral-large-2512",     # Strong writing
    "ViralMarketer":    "meta-llama/llama-4-maverick",      # Edgy, creative
    "Skeptic":          "deepseek/deepseek-r1",             # Deep reasoning for ROI analysis

    # ── Research Department ──
    # Need deep reasoning and broad knowledge
    "DeepDiver":        "deepseek/deepseek-r1",             # Best reasoning model
    "TrendSpotter":     "google/gemini-2.5-pro",            # Broad knowledge base
    "Synthesizer":      "anthropic/claude-sonnet-4.6",      # Cross-domain connections
    "FactChecker":      "deepseek/deepseek-v3.2",           # Precise verification

    # ── Finance Department ──
    # Conservative, precise, quantitative
    "CFO":              "anthropic/claude-sonnet-4.6",      # Careful, thorough analysis
    "RiskAnalyst":      "deepseek/deepseek-r1",             # Deep scenario modeling
    "RevenueStrategist": "google/gemini-2.5-flash",         # Fast revenue modeling
    "TaxOptimizer":     "mistralai/mistral-large-2512",     # Precise, detail-oriented
    "Auditor":          "deepseek/deepseek-v3.2",           # Thorough verification

    # ── Engineering Department ──
    # Technical depth, code-aware models
    "CTO":              "anthropic/claude-sonnet-4.6",      # Best for architecture decisions
    "BackendLead":      "deepseek/deepseek-v3.2",           # Strong backend reasoning
    "FrontendLead":     "qwen/qwen3-coder-next",            # Code-aware, frontend
    "DevOps":           "google/gemini-2.5-flash",          # Practical infrastructure
    "SecurityEngineer": "mistralai/mistral-large-2512",     # Security-focused precision

    # ── Legal Department ──
    # Precise, conservative, detail-oriented
    "GeneralCounsel":   "anthropic/claude-sonnet-4.6",      # Careful legal reasoning
    "IPAttorney":       "deepseek/deepseek-r1",             # Deep IP analysis
    "ComplianceOfficer": "mistralai/mistral-large-2512",    # European compliance perspective
    "ContractReviewer": "google/gemini-2.5-pro",            # Detailed contract analysis

    # ── Operations Department ──
    # Execution-focused, practical
    "COO":              "anthropic/claude-haiku-4.5",       # Fast, decisive
    "SupplyChain":      "deepseek/deepseek-v3.2",           # Logistics optimization
    "HRDirector":       "mistralai/mistral-small-creative",  # People-focused, empathetic
    "ProcessEngineer":  "qwen/qwen3-coder-plus",            # Process automation expert

    # ── Sales Department ──
    # Persuasive, customer-aware
    "VPSales":          "meta-llama/llama-4-maverick",      # Bold, sales-oriented
    "AccountExecutive": "anthropic/claude-haiku-4.5",       # Empathetic, fast
    "SalesEngineer":    "deepseek/deepseek-v3.2",           # Technical depth
    "CustomerSuccess":  "google/gemini-2.5-flash",          # Broad customer understanding

    # ── Creative Department ──
    # Maximum creative diversity
    "CreativeDirector": "mistralai/mistral-small-creative",  # Purpose-built for creative
    "BrandStrategist":  "anthropic/claude-sonnet-4.6",      # Deep brand analysis
    "ContentLead":      "meta-llama/llama-4-maverick",      # Bold content takes
}


def get_openrouter_model(agent_name: str) -> str:
    """Get the OpenRouter model for an agent, with fallback."""
    return OPENROUTER_MODELS.get(agent_name, "deepseek/deepseek-v3.2")


def remap_agents_to_openrouter(agents: list) -> list:
    """Create copies of agents with OpenRouter model assignments."""
    remapped = []
    for agent in agents:
        new_agent = type(agent)(
            name=agent.name,
            role=agent.role,
            expertise=agent.expertise,
            bias=agent.bias,
            system_prompt=agent.system_prompt,
            model=get_openrouter_model(agent.name),
        )
        remapped.append(new_agent)
    return remapped
