"""Tests for tool registry and built-in tools."""

import pytest

from swarm_agency.tools import (
    ToolDefinition,
    ToolCall,
    ToolResult,
    ToolRegistry,
    _math_eval,
    _percentage,
    _compound_growth,
    _roi_calculator,
    _break_even,
    default_registry,
)


class TestMathEval:
    def test_basic_arithmetic(self):
        assert _math_eval("2 + 3") == "5"
        assert _math_eval("10 * 5") == "50"
        assert _math_eval("100 / 4") in ("25", "25.0")

    def test_complex_expression(self):
        result = float(_math_eval("1000 * 0.15 * 12"))
        assert result == pytest.approx(1800.0)

    def test_parentheses(self):
        assert _math_eval("(2 + 3) * 4") == "20"

    def test_invalid_expression(self):
        result = _math_eval("import os")
        assert "Error" in result or result == ""

    def test_empty_expression(self):
        result = _math_eval("")
        assert "Error" in result or "invalid" in result.lower()

    def test_percentage_syntax(self):
        result = float(_math_eval("50%"))
        assert result == pytest.approx(0.5)


class TestPercentage:
    def test_basic(self):
        assert "50.00%" in _percentage("50", "100")

    def test_zero_total(self):
        assert "Error" in _percentage("50", "0")

    def test_invalid_input(self):
        assert "Error" in _percentage("abc", "100")


class TestCompoundGrowth:
    def test_basic(self):
        result = _compound_growth("1000", "10", "1")
        assert "$1,100.00" in result

    def test_multi_year(self):
        result = _compound_growth("1000", "10", "2")
        assert "$1,210.00" in result

    def test_invalid(self):
        assert "Error" in _compound_growth("abc", "10", "1")


class TestROI:
    def test_positive_roi(self):
        result = _roi_calculator("1000", "1500")
        assert "50.0%" in result

    def test_negative_roi(self):
        result = _roi_calculator("1000", "500")
        assert "-50.0%" in result

    def test_zero_investment(self):
        assert "Error" in _roi_calculator("0", "100")


class TestBreakEven:
    def test_basic(self):
        result = _break_even("10000", "100", "60")
        assert "250" in result  # 10000 / (100-60) = 250

    def test_negative_margin(self):
        assert "Error" in _break_even("10000", "50", "60")


class TestToolRegistry:
    def test_builtins_registered(self):
        registry = ToolRegistry()
        tools = registry.list_tools()
        assert "calculate" in tools
        assert "percentage" in tools
        assert "compound_growth" in tools
        assert "roi" in tools
        assert "break_even" in tools

    def test_execute_calculate(self):
        registry = ToolRegistry()
        result = registry.execute("calculate", {"expression": "2 + 3"})
        assert result.success is True
        assert result.result == "5"

    def test_execute_unknown_tool(self):
        registry = ToolRegistry()
        result = registry.execute("nonexistent", {})
        assert result.success is False
        assert "Unknown" in result.result

    def test_register_custom_tool(self):
        registry = ToolRegistry()
        registry.register(ToolDefinition(
            name="greet",
            description="Say hello",
            parameters={"name": "Who to greet"},
            handler=lambda name="World": f"Hello, {name}!",
        ))
        result = registry.execute("greet", {"name": "Miles"})
        assert result.success is True
        assert "Hello, Miles!" in result.result

    def test_budget_control(self):
        registry = ToolRegistry()
        registry._budget_limit = 0.05
        registry.register(ToolDefinition(
            name="expensive",
            description="Costs money",
            parameters={},
            handler=lambda: "result",
            cost=0.03,
        ))
        # First call succeeds
        r1 = registry.execute("expensive", {})
        assert r1.success is True
        # Second call exceeds budget
        r2 = registry.execute("expensive", {})
        assert r2.success is False
        assert "Budget" in r2.result

    def test_execute_batch(self):
        registry = ToolRegistry()
        calls = [
            {"name": "calculate", "args": {"expression": "1+1"}},
            {"name": "calculate", "args": {"expression": "2*3"}},
        ]
        result = registry.execute_batch(calls)
        assert len(result.calls) == 2
        assert result.calls[0].result == "2"
        assert result.calls[1].result == "6"

    def test_batch_max_five(self):
        registry = ToolRegistry()
        calls = [{"name": "calculate", "args": {"expression": f"{i}+1"}} for i in range(10)]
        result = registry.execute_batch(calls)
        assert len(result.calls) == 5  # capped at 5

    def test_get_tool_descriptions(self):
        registry = ToolRegistry()
        desc = registry.get_tool_descriptions()
        assert "calculate" in desc
        assert "tool_calls" in desc

    def test_reset_budget(self):
        registry = ToolRegistry()
        registry._budget_used = 0.5
        registry.reset_budget()
        assert registry.budget_remaining == registry._budget_limit

    def test_tool_result_to_context(self):
        result = ToolResult(calls=[
            ToolCall(tool_name="calculate", arguments={"expression": "1+1"}, result="2", success=True),
        ])
        ctx = result.to_context()
        assert "Tool Results" in ctx
        assert "calculate" in ctx
        assert "OK" in ctx

    def test_empty_tool_result_context(self):
        result = ToolResult()
        assert result.to_context() == ""


class TestDefaultRegistry:
    def test_exists(self):
        assert default_registry is not None
        assert len(default_registry.list_tools()) >= 5
