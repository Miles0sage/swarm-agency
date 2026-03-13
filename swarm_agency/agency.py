"""Agency - the top-level orchestrator of departments."""

import asyncio
import logging
import os
from typing import Optional

from .types import AgencyRequest, Decision
from .department import Department

logger = logging.getLogger("swarm_agency.agency")


class Agency:
    """An AI agency composed of departments that debate decisions."""

    def __init__(
        self,
        name: str = "Agency",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.name = name
        self.api_key = api_key or os.environ.get("ALIBABA_CODING_API_KEY", "")
        self.base_url = base_url or os.environ.get(
            "ALIBABA_CODING_BASE_URL",
            "https://coding-intl.dashscope.aliyuncs.com/v1",
        )
        self.departments: dict[str, Department] = {}

    def add_department(self, department: Department) -> None:
        """Register a department with the agency."""
        department.api_key = self.api_key
        department.base_url = self.base_url
        self.departments[department.name] = department

    def remove_department(self, name: str) -> None:
        """Remove a department by name."""
        self.departments.pop(name, None)

    def list_departments(self) -> list[str]:
        """Return list of department names."""
        return list(self.departments.keys())

    async def consult(
        self,
        request: AgencyRequest,
        departments: Optional[list[str]] = None,
    ) -> list[Decision]:
        """
        Consult one or more departments about a request.

        If request.department is set, only that department debates.
        If departments list is provided, those departments debate in parallel.
        Otherwise, all departments debate in parallel.
        """
        target_depts = self._resolve_departments(request, departments)

        if not target_depts:
            logger.warning("No departments to consult")
            return []

        tasks = [dept.debate(request) for dept in target_depts]
        decisions = await asyncio.gather(*tasks)
        return list(decisions)

    async def decide(
        self,
        request: AgencyRequest,
        departments: Optional[list[str]] = None,
    ) -> Decision:
        """
        Get a single consolidated decision from the agency.

        If multiple departments are consulted, their decisions are synthesized
        into one agency-level decision.
        """
        decisions = await self.consult(request, departments)

        if not decisions:
            return Decision(
                request_id=request.request_id,
                department=self.name,
                outcome="DEADLOCK",
                position="NONE",
                confidence=0.0,
                summary="No departments available.",
            )

        if len(decisions) == 1:
            return decisions[0]

        return self._synthesize(decisions, request)

    def _resolve_departments(
        self,
        request: AgencyRequest,
        departments: Optional[list[str]],
    ) -> list[Department]:
        """Resolve which departments to consult."""
        if request.department:
            dept = self.departments.get(request.department)
            return [dept] if dept else []

        if departments:
            return [
                self.departments[name]
                for name in departments
                if name in self.departments
            ]

        return list(self.departments.values())

    def _synthesize(
        self, decisions: list[Decision], request: AgencyRequest
    ) -> Decision:
        """Synthesize multiple department decisions into one agency decision."""
        all_votes = []
        all_dissents = []
        total_duration = 0.0

        position_weights: dict[str, float] = {}
        for d in decisions:
            all_votes.extend(d.votes)
            all_dissents.extend(d.dissenting_views)
            total_duration = max(total_duration, d.duration_seconds)

            weight = d.confidence
            position_weights[d.position] = (
                position_weights.get(d.position, 0.0) + weight
            )

        if not position_weights:
            return Decision(
                request_id=request.request_id,
                department=self.name,
                outcome="DEADLOCK",
                position="NONE",
                confidence=0.0,
                summary="No positions from any department.",
            )

        # Winner by weighted confidence
        top_position = max(position_weights, key=position_weights.get)
        agreeing = [d for d in decisions if d.position == top_position]
        total_depts = len(decisions)
        agree_count = len(agreeing)
        avg_conf = sum(d.confidence for d in agreeing) / agree_count

        if agree_count == total_depts:
            outcome = "CONSENSUS"
            summary = (
                f"All {total_depts} departments agree: {top_position}."
            )
        elif agree_count > total_depts / 2:
            outcome = "MAJORITY"
            summary = (
                f"{agree_count}/{total_depts} departments favor {top_position}."
            )
        else:
            outcome = "SPLIT"
            dept_positions = ", ".join(
                f"{d.department}: {d.position}" for d in decisions
            )
            summary = f"Departments split: {dept_positions}."

        return Decision(
            request_id=request.request_id,
            department=self.name,
            outcome=outcome,
            position=top_position,
            confidence=round(avg_conf * (agree_count / total_depts), 3),
            votes=all_votes,
            summary=summary,
            dissenting_views=all_dissents,
            duration_seconds=round(total_duration, 2),
        )
