"""Agency - the top-level orchestrator of departments."""

import asyncio
import logging
import os
from typing import Optional

import numpy as np

from .types import AgencyRequest, Decision, DecisionRecord
from .department import Department
from .memory import DecisionMemoryStore, DEFAULT_MEMORY_PATH

logger = logging.getLogger("swarm_agency.agency")


class Agency:
    """An AI agency composed of departments that debate decisions."""

    def __init__(
        self,
        name: str = "Agency",
        api_key: str | None = None,
        base_url: str | None = None,
        memory_enabled: bool = False,
        memory_path: str | None = None,
        provider: str | None = None,
        gemini_api_key: str | None = None,
    ):
        self.name = name
        self.provider = provider or "dashscope"

        # Resolve API key and base URL from provider
        if self.provider == "openrouter":
            self.api_key = (api_key or os.environ.get("OPENROUTER_API_KEY", "")).strip()
            self.base_url = base_url or "https://openrouter.ai/api/v1"
        else:
            self.api_key = (api_key or os.environ.get("ALIBABA_CODING_API_KEY", "")).strip()
            self.base_url = base_url or os.environ.get(
                "ALIBABA_CODING_BASE_URL",
                "https://coding-intl.dashscope.aliyuncs.com/v1",
            )
        self.gemini_api_key = (
            gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
        ).strip()
        self.departments: dict[str, Department] = {}
        self._dept_embeddings: dict[str, np.ndarray] = {}
        self.memory_enabled = memory_enabled
        self._memory_store: Optional[DecisionMemoryStore] = None
        if memory_enabled:
            self._memory_store = DecisionMemoryStore(
                db_path=memory_path or DEFAULT_MEMORY_PATH
            )

    def add_department(self, department: Department) -> None:
        """Register a department with the agency."""
        # Remap models when using OpenRouter
        if self.provider == "openrouter":
            from .providers import remap_agents_to_openrouter
            department.agents = remap_agents_to_openrouter(department.agents)

        department.api_key = self.api_key
        department.base_url = self.base_url
        self.departments[department.name] = department

    def remove_department(self, name: str) -> None:
        """Remove a department by name."""
        self.departments.pop(name, None)

    def list_departments(self) -> list[str]:
        """Return list of department names."""
        return list(self.departments.keys())

    @property
    def memory_store(self) -> Optional[DecisionMemoryStore]:
        """Access the memory store (if enabled)."""
        return self._memory_store

    def feedback(self, request_id: str, was_correct: bool, notes: Optional[str] = None) -> bool:
        """Record feedback on a past decision."""
        if not self._memory_store:
            logger.warning("Memory not enabled — feedback ignored")
            return False
        return self._memory_store.add_feedback(request_id, was_correct, notes)

    def history(self, department: Optional[str] = None, limit: int = 20) -> list[DecisionRecord]:
        """Get decision history."""
        if not self._memory_store:
            return []
        return self._memory_store.get_history(department, limit)

    async def route_to_departments(
        self,
        question: str,
        threshold: float = 0.3,
        max_departments: int = 3,
    ) -> list[str]:
        """Auto-route a question to the most relevant departments using embeddings.

        Returns department names sorted by relevance. Falls back to all
        departments if embedding fails.
        """
        if not self.gemini_api_key or not self.departments:
            return list(self.departments.keys())

        from .embeddings import get_embedding, cosine_similarity

        query_emb = await get_embedding(question, self.gemini_api_key)
        if query_emb is None:
            return list(self.departments.keys())

        query_vec = np.array(query_emb, dtype=np.float32)

        # Cache department description embeddings
        if not self._dept_embeddings:
            for dept_name, dept in self.departments.items():
                if dept.description:
                    emb = await get_embedding(dept.description, self.gemini_api_key)
                    if emb is not None:
                        self._dept_embeddings[dept_name] = np.array(emb, dtype=np.float32)

        if not self._dept_embeddings:
            return list(self.departments.keys())

        scored = []
        for dept_name, dept_vec in self._dept_embeddings.items():
            score = cosine_similarity(query_vec, dept_vec)
            if score >= threshold:
                scored.append((score, dept_name))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            return list(self.departments.keys())

        return [name for _, name in scored[:max_departments]]

    async def consult(
        self,
        request: AgencyRequest,
        departments: Optional[list[str]] = None,
    ) -> list[Decision]:
        """
        Consult one or more departments about a request.

        If request.department is set, only that department debates.
        If departments list is provided, those departments debate in parallel.
        Otherwise, auto-routes to relevant departments (or all if no embedding key).
        """
        # Pre-compute query embedding once for reuse
        query_embedding = None
        if self.gemini_api_key and self.memory_enabled:
            from .embeddings import get_embedding
            query_embedding = await get_embedding(
                request.question, self.gemini_api_key
            )

        target_depts = self._resolve_departments(request, departments)

        # Auto-route if no specific department requested
        if not request.department and not departments and self.gemini_api_key:
            routed = await self.route_to_departments(request.question)
            target_depts = [
                self.departments[n] for n in routed if n in self.departments
            ]

        if not target_depts:
            logger.warning("No departments to consult")
            return []

        tasks = [
            dept.debate(
                request,
                memory_store=self._memory_store,
                query_embedding=query_embedding,
            )
            for dept in target_depts
        ]
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
            decision = decisions[0]
        else:
            decision = self._synthesize(decisions, request)

        # Pre-compute embedding for storage
        embedding = None
        if self.gemini_api_key:
            from .embeddings import get_embedding
            embedding = await get_embedding(
                request.question, self.gemini_api_key
            )

        # Auto-store in memory
        if self._memory_store:
            try:
                self._memory_store.store_decision(
                    decision, request.question, request.context,
                    embedding=embedding,
                )
            except Exception as e:
                logger.warning(f"Failed to store decision in memory: {e}")

        return decision

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
