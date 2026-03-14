"""Single agent caller - makes one API call per agent."""

import json
import logging
import re

import httpx

from .types import AgentConfig, AgencyRequest, AgentVote

logger = logging.getLogger("swarm_agency.agent")


def _extract_json(text: str) -> dict:
    """Extract a JSON object from messy LLM output.

    Handles: markdown fences, text before/after JSON, nested braces,
    truncated JSON, thinking tokens, escaped quotes.
    """
    # Strip markdown fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    # Try direct parse first (fastest path)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Find the outermost { } with brace matching
    depth = 0
    start = -1
    for i, ch in enumerate(cleaned):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth > 0:
            depth -= 1
            if depth == 0:
                candidate = cleaned[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

    # Brace matching failed — try simple first { to last }
    json_start = cleaned.find("{")
    json_end = cleaned.rfind("}")
    if json_start >= 0 and json_end > json_start:
        candidate = cleaned[json_start:json_end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Last resort: regex extract key fields
    position = "MAYBE"
    confidence = 0.5
    reasoning = "Response could not be parsed"
    factors = []

    pos_match = re.search(r'"position"\s*:\s*"([^"]+)"', cleaned)
    if pos_match:
        position = pos_match.group(1)
    conf_match = re.search(r'"confidence"\s*:\s*([\d.]+)', cleaned)
    if conf_match:
        confidence = float(conf_match.group(1))
    reason_match = re.search(r'"reasoning"\s*:\s*"((?:[^"\\]|\\.)*)"', cleaned)
    if reason_match:
        reasoning = reason_match.group(1)
    factors_match = re.search(r'"factors"\s*:\s*\[(.*?)\]', cleaned, re.DOTALL)
    if factors_match:
        factors = [f.strip().strip('"') for f in factors_match.group(1).split(",") if f.strip().strip('"')]

    return {
        "position": position,
        "confidence": confidence,
        "reasoning": reasoning,
        "factors": factors,
    }

DEFAULT_TIMEOUT = 90.0


def format_agent_prompt(
    agent: AgentConfig,
    request: AgencyRequest,
    memory_context: str = "",
) -> str:
    """Format the user prompt for an agent given a request."""
    lines = [
        f"## Decision Required",
        f"",
        f"**Question:** {request.question}",
    ]
    if request.context:
        lines.append(f"**Context:** {request.context}")
    if request.metadata:
        for k, v in request.metadata.items():
            lines.append(f"**{k}:** {v}")

    if memory_context:
        lines.extend(["", memory_context])

    lines.extend([
        "",
        f"You are the **{agent.role}** with expertise in {agent.expertise}.",
        f"Your analytical bias: {agent.bias}",
        "",
        "Your `position` MUST be exactly one of: YES, NO, or MAYBE.",
        "",
        "IMPORTANT: Respond with ONLY a JSON object. No explanation before or after. No markdown. No thinking. Just the JSON:",
        '{"position": "YES", "confidence": 0.85, "reasoning": "2-3 sentences max", "factors": ["factor1", "factor2"], "dissent": "only if you disagree"}',
    ])
    return "\n".join(lines)


async def call_agent(
    agent: AgentConfig,
    request: AgencyRequest,
    api_key: str,
    base_url: str,
    memory_context: str = "",
) -> AgentVote:
    """Call API with an agent's system prompt and return an AgentVote."""
    user_prompt = format_agent_prompt(agent, request, memory_context)

    payload = {
        "model": agent.model,
        "messages": [
            {"role": "system", "content": agent.system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }

    # Request JSON output format — skip for models that don't support it
    # Gemini models on OpenRouter don't handle response_format well
    model_lower = agent.model.lower()
    gemini_model = "gemini" in model_lower or "google" in model_lower
    if ("openrouter" in base_url or "openai" in base_url) and not gemini_model:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }

    url = f"{base_url}/chat/completions"

    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()

            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            parsed = _extract_json(content)

            # Check if we got a real parse or fallback
            reasoning = parsed.get("reasoning", "No reasoning provided")
            if reasoning == "Response could not be parsed" and attempt == 0:
                # Retry with a clean, short request
                logger.warning(f"{agent.name} returned unparseable response, retrying with strict prompt")
                payload["messages"] = [
                    {"role": "system", "content": "You are a business analyst. Respond with ONLY valid JSON."},
                    {"role": "user", "content": (
                        f"Question: {request.question}\n"
                        f"Vote YES, NO, or MAYBE. Reply ONLY with this JSON:\n"
                        f'{{"position": "YES", "confidence": 0.8, "reasoning": "your 1-2 sentence reason", "factors": ["f1"]}}'
                    )},
                ]
                payload.pop("response_format", None)  # remove in case it caused issues
                continue

            return AgentVote(
                agent_name=agent.name,
                position=str(parsed.get("position", "ABSTAIN")).upper(),
                confidence=max(0.0, min(1.0, float(parsed.get("confidence", 0.5)))),
                reasoning=reasoning,
                factors=parsed.get("factors", []),
                dissent=parsed.get("dissent"),
            )

        except Exception as e:
            if attempt == 0:
                logger.warning(f"{agent.name} attempt 1 failed: {e}, retrying...")
                continue
            logger.error(f"{agent.name} failed after 2 attempts: {e}")
            return AgentVote(
                agent_name=agent.name,
                position="ERROR",
                confidence=0.0,
                reasoning=f"API call failed: {str(e)[:100]}",
                factors=["error"],
            )
