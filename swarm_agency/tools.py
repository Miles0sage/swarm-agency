"""Tool registry — optional tools that agents can call during debate.

Agents decide whether to use tools based on the question. Tools are sandboxed
and budget-controlled. Currently supports: web search, math, memory lookup.
"""

import json
import logging
import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger("swarm_agency.tools")


@dataclass
class ToolDefinition:
    """A tool agents can optionally invoke."""
    name: str
    description: str
    parameters: dict[str, str]  # param_name → description
    handler: Callable  # sync function that executes the tool
    cost: float = 0.0  # estimated cost per call in USD


@dataclass
class ToolCall:
    """Record of a tool invocation."""
    tool_name: str
    arguments: dict[str, Any]
    result: str
    success: bool


@dataclass
class ToolResult:
    """Aggregated tool results for an agent."""
    calls: list[ToolCall] = field(default_factory=list)
    total_cost: float = 0.0

    def to_context(self) -> str:
        """Format tool results as context for the agent."""
        if not self.calls:
            return ""
        lines = ["\n## Tool Results\n"]
        for call in self.calls:
            status = "OK" if call.success else "FAILED"
            lines.append(f"**{call.tool_name}** [{status}]: {call.result[:500]}")
        return "\n".join(lines)


# ── Built-in Tools ──────────────────────────────────────────────────

def _math_eval(expression: str) -> str:
    """Safe math evaluation using AST walking — no exec/eval."""
    import ast
    import operator

    # Replace common patterns before parsing
    cleaned = expression.strip()
    if not cleaned:
        return "Error: invalid expression"
    cleaned = cleaned.replace('%', '/100')
    # Remove anything that's not math-safe
    cleaned = re.sub(r'[^0-9+\-*/().,\s]', '', cleaned)
    if not cleaned.strip():
        return "Error: invalid expression"

    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _eval_node(node):
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            return ops[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](_eval_node(node.operand))
        raise ValueError(f"Unsupported: {ast.dump(node)}")

    try:
        tree = ast.parse(cleaned, mode='eval')
        result = _eval_node(tree)
        # Return clean int if possible
        if isinstance(result, float) and result == int(result) and abs(result) < 1e15:
            return str(int(result))
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def _percentage(value: str, total: str) -> str:
    """Calculate percentage."""
    try:
        v = float(value)
        t = float(total)
        if t == 0:
            return "Error: division by zero"
        return f"{(v / t) * 100:.2f}%"
    except ValueError:
        return "Error: invalid numbers"


def _compound_growth(principal: str, rate: str, years: str) -> str:
    """Calculate compound growth."""
    try:
        p = float(principal)
        r = float(rate) / 100
        y = float(years)
        result = p * (1 + r) ** y
        return f"${result:,.2f} (from ${p:,.2f} at {r*100:.1f}% over {y:.0f} years)"
    except (ValueError, OverflowError) as e:
        return f"Error: {e}"


def _roi_calculator(investment: str, returns: str) -> str:
    """Calculate ROI."""
    try:
        inv = float(investment)
        ret = float(returns)
        if inv == 0:
            return "Error: zero investment"
        roi = ((ret - inv) / inv) * 100
        return f"ROI: {roi:.1f}% (invested ${inv:,.0f}, returned ${ret:,.0f})"
    except ValueError:
        return "Error: invalid numbers"


def _break_even(fixed_costs: str, price_per_unit: str, cost_per_unit: str) -> str:
    """Calculate break-even point."""
    try:
        fc = float(fixed_costs)
        ppu = float(price_per_unit)
        cpu = float(cost_per_unit)
        margin = ppu - cpu
        if margin <= 0:
            return "Error: price must exceed cost per unit"
        units = math.ceil(fc / margin)
        return f"Break-even at {units:,} units (${fc:,.0f} fixed / ${margin:.2f} margin per unit)"
    except ValueError:
        return "Error: invalid numbers"


# ── Tool Registry ───────────────────────────────────────────────────

class ToolRegistry:
    """Registry of available tools for agents."""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
        self._budget_limit: float = 1.0  # max USD per debate
        self._budget_used: float = 0.0
        self._register_builtins()

    def _register_builtins(self):
        """Register built-in tools."""
        self.register(ToolDefinition(
            name="calculate",
            description="Evaluate a math expression (arithmetic only, no variables)",
            parameters={"expression": "Math expression like '1000 * 0.15 * 12'"},
            handler=lambda expression="0": _math_eval(expression),
        ))
        self.register(ToolDefinition(
            name="percentage",
            description="Calculate what percentage value is of total",
            parameters={"value": "The part", "total": "The whole"},
            handler=lambda value="0", total="1": _percentage(value, total),
        ))
        self.register(ToolDefinition(
            name="compound_growth",
            description="Calculate compound growth over time",
            parameters={
                "principal": "Starting amount",
                "rate": "Annual growth rate as percentage",
                "years": "Number of years",
            },
            handler=lambda principal="0", rate="0", years="0": _compound_growth(
                principal, rate, years
            ),
        ))
        self.register(ToolDefinition(
            name="roi",
            description="Calculate return on investment",
            parameters={"investment": "Amount invested", "returns": "Amount returned"},
            handler=lambda investment="0", returns="0": _roi_calculator(investment, returns),
        ))
        self.register(ToolDefinition(
            name="break_even",
            description="Calculate break-even point in units",
            parameters={
                "fixed_costs": "Total fixed costs",
                "price_per_unit": "Selling price per unit",
                "cost_per_unit": "Variable cost per unit",
            },
            handler=lambda fixed_costs="0", price_per_unit="0", cost_per_unit="0": _break_even(
                fixed_costs, price_per_unit, cost_per_unit
            ),
        ))
        self.register(ToolDefinition(
            name="web_search",
            description="Search the web for current information, news, data, or facts",
            parameters={"query": "Search query"},
            handler=lambda query="": _web_search_handler(query),
        ))

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List registered tool names."""
        return list(self._tools.keys())

    def get_tool_descriptions(self) -> str:
        """Format tool descriptions for injection into agent prompts."""
        if not self._tools:
            return ""

        lines = ["\n## Available Tools\n"]
        lines.append("You may optionally request tool calls by including a `tool_calls` array in your JSON response.")
        lines.append("Each tool call: `{\"name\": \"tool_name\", \"args\": {\"param\": \"value\"}}`")
        lines.append("Tool results will be provided if you request them.\n")

        for name, tool in self._tools.items():
            params = ", ".join(f"{k}: {v}" for k, v in tool.parameters.items())
            lines.append(f"- **{name}**: {tool.description} ({params})")

        return "\n".join(lines)

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> ToolCall:
        """Execute a tool call."""
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolCall(
                tool_name=tool_name,
                arguments=arguments,
                result=f"Unknown tool: {tool_name}",
                success=False,
            )

        if self._budget_used + tool.cost > self._budget_limit:
            return ToolCall(
                tool_name=tool_name,
                arguments=arguments,
                result="Budget exceeded",
                success=False,
            )

        try:
            result = tool.handler(**arguments)
            self._budget_used += tool.cost
            return ToolCall(
                tool_name=tool_name,
                arguments=arguments,
                result=str(result),
                success=True,
            )
        except Exception as e:
            return ToolCall(
                tool_name=tool_name,
                arguments=arguments,
                result=f"Error: {e}",
                success=False,
            )

    def execute_batch(self, calls: list[dict]) -> ToolResult:
        """Execute multiple tool calls and return aggregated results."""
        result = ToolResult()
        for call_spec in calls[:5]:  # Max 5 tool calls per agent
            name = call_spec.get("name", "")
            args = call_spec.get("args", {})
            call = self.execute(name, args)
            result.calls.append(call)
            result.total_cost += self._tools.get(name, ToolDefinition(
                name="", description="", parameters={}, handler=lambda: "",
            )).cost
        return result

    def reset_budget(self):
        """Reset the budget counter."""
        self._budget_used = 0.0

    @property
    def budget_remaining(self) -> float:
        return self._budget_limit - self._budget_used


def _web_search_handler(query: str = "") -> str:
    """Synchronous wrapper for web search (runs in tools context)."""
    import asyncio
    from .web_search import web_search
    try:
        loop = asyncio.get_running_loop()
        # If already in async context, create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = pool.submit(asyncio.run, web_search(query)).result(timeout=15)
        return result
    except RuntimeError:
        return asyncio.run(web_search(query))
    except Exception as e:
        return f"Search failed: {e}"


# Default global registry
default_registry = ToolRegistry()
