"""Autonomous Agent Scheduler — agents run jobs on cron, not on-demand.

Each agent can have scheduled tasks:
- CFO checks revenue metrics daily
- CTO scans for CVEs weekly
- DevilsAdvocate challenges the week's top decision

Jobs run in the background, results go through the debate pipeline,
and alerts are pushed to the user via configured channels.
"""

import asyncio
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from .types import AgencyRequest, Decision

logger = logging.getLogger("swarm_agency.scheduler")

JOBS_FILE = os.path.expanduser("~/.swarm-agency/scheduled_jobs.json")


@dataclass
class ScheduledJob:
    """A recurring job for an agent or department."""
    job_id: str
    name: str
    description: str
    department: Optional[str]  # None = all departments
    question_template: str  # can include {date}, {day_of_week}
    context_template: str
    schedule: str  # "daily", "weekly", "hourly", "every_N_hours"
    interval_hours: float  # actual interval in hours
    enabled: bool = True
    last_run: float = 0.0
    last_result: Optional[str] = None
    notify: bool = True  # push alert on completion
    run_count: int = 0


@dataclass
class JobResult:
    """Result of a scheduled job execution."""
    job_id: str
    job_name: str
    decision: Decision
    timestamp: float
    duration: float
    alert_sent: bool = False


# ── Default Jobs ─────────────────────────────────────────────────

DEFAULT_JOBS = [
    ScheduledJob(
        job_id="daily-health-check",
        name="Daily Business Health Check",
        description="CFO reviews key metrics and flags concerns",
        department="Finance",
        question_template="Based on current business trajectory, what are the top 3 risks and opportunities we should address today ({date})?",
        context_template="This is a proactive daily check. Flag anything that needs attention. Be specific about numbers and timelines.",
        schedule="daily",
        interval_hours=24.0,
    ),
    ScheduledJob(
        job_id="weekly-strategy-review",
        name="Weekly Strategy Review",
        description="Strategy team reviews the week's decisions and course-corrects",
        department="Strategy",
        question_template="Review this week's decisions and market developments. Should we change direction on anything? What opportunities are we missing?",
        context_template="Weekly strategic review for {day_of_week}. Consider market changes, competitive moves, and internal progress.",
        schedule="weekly",
        interval_hours=168.0,
    ),
    ScheduledJob(
        job_id="devils-advocate-challenge",
        name="Devil's Advocate Challenge",
        description="DevilsAdvocate challenges the most recent major decision",
        department="Strategy",
        question_template="Challenge our most recent decision. What could go wrong? What are we not seeing? Play the strongest possible case AGAINST our current direction.",
        context_template="Proactive adversarial review. Be brutally honest. Find the blind spots.",
        schedule="weekly",
        interval_hours=168.0,
    ),
    ScheduledJob(
        job_id="engineering-debt-scan",
        name="Technical Debt Scan",
        description="Engineering team reviews tech debt and security",
        department="Engineering",
        question_template="What technical risks are accumulating? Are there security vulnerabilities, scaling bottlenecks, or architectural decisions we should revisit?",
        context_template="Proactive engineering review. Focus on what breaks at 10x scale.",
        schedule="weekly",
        interval_hours=168.0,
    ),
]


class AgentScheduler:
    """Manages and executes scheduled agent jobs."""

    def __init__(self, agency=None, jobs_file: str = JOBS_FILE):
        self.agency = agency
        self.jobs_file = jobs_file
        self.jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._alert_handlers: list[Callable] = []
        self._load_jobs()

    def _load_jobs(self) -> None:
        """Load jobs from disk."""
        path = Path(self.jobs_file)
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for jd in data:
                    job = ScheduledJob(**jd)
                    self.jobs[job.job_id] = job
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to load jobs: {e}")

        # Add defaults if not present
        for default in DEFAULT_JOBS:
            if default.job_id not in self.jobs:
                self.jobs[default.job_id] = default

    def _save_jobs(self) -> None:
        """Persist jobs to disk."""
        path = Path(self.jobs_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for job in self.jobs.values():
            data.append({
                "job_id": job.job_id,
                "name": job.name,
                "description": job.description,
                "department": job.department,
                "question_template": job.question_template,
                "context_template": job.context_template,
                "schedule": job.schedule,
                "interval_hours": job.interval_hours,
                "enabled": job.enabled,
                "last_run": job.last_run,
                "last_result": job.last_result,
                "notify": job.notify,
                "run_count": job.run_count,
            })
        path.write_text(json.dumps(data, indent=2))

    def add_job(self, job: ScheduledJob) -> None:
        self.jobs[job.job_id] = job
        self._save_jobs()

    def remove_job(self, job_id: str) -> bool:
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save_jobs()
            return True
        return False

    def enable_job(self, job_id: str) -> bool:
        if job_id in self.jobs:
            self.jobs[job_id].enabled = True
            self._save_jobs()
            return True
        return False

    def disable_job(self, job_id: str) -> bool:
        if job_id in self.jobs:
            self.jobs[job_id].enabled = False
            self._save_jobs()
            return True
        return False

    def list_jobs(self) -> list[ScheduledJob]:
        return list(self.jobs.values())

    def on_alert(self, handler: Callable) -> None:
        """Register an alert handler. Called with (job, decision) when a job completes."""
        self._alert_handlers.append(handler)

    def get_due_jobs(self) -> list[ScheduledJob]:
        """Get jobs that are due to run."""
        now = time.time()
        due = []
        for job in self.jobs.values():
            if not job.enabled:
                continue
            elapsed = now - job.last_run
            if elapsed >= job.interval_hours * 3600:
                due.append(job)
        return due

    async def run_job(self, job: ScheduledJob) -> Optional[JobResult]:
        """Execute a single scheduled job."""
        if not self.agency:
            logger.warning("No agency configured for scheduler")
            return None

        from datetime import datetime
        now = datetime.now()
        question = job.question_template.format(
            date=now.strftime("%Y-%m-%d"),
            day_of_week=now.strftime("%A"),
        )
        context = job.context_template.format(
            date=now.strftime("%Y-%m-%d"),
            day_of_week=now.strftime("%A"),
        )

        request = AgencyRequest(
            request_id=f"sched-{job.job_id}-{uuid.uuid4().hex[:6]}",
            question=question,
            context=context,
            department=job.department,
            metadata={"scheduled_job": job.job_id, "job_name": job.name},
        )

        start = time.time()
        try:
            decision = await self.agency.decide(request)
            duration = time.time() - start

            job.last_run = time.time()
            job.last_result = f"{decision.outcome}: {decision.position} ({decision.confidence:.0%})"
            job.run_count += 1
            self._save_jobs()

            result = JobResult(
                job_id=job.job_id,
                job_name=job.name,
                decision=decision,
                timestamp=time.time(),
                duration=duration,
            )

            # Fire alert handlers
            if job.notify:
                for handler in self._alert_handlers:
                    try:
                        handler(job, decision)
                        result.alert_sent = True
                    except Exception as e:
                        logger.warning(f"Alert handler failed: {e}")

            return result

        except Exception as e:
            logger.error(f"Job {job.job_id} failed: {e}")
            job.last_run = time.time()
            job.last_result = f"ERROR: {str(e)[:100]}"
            self._save_jobs()
            return None

    async def run_due_jobs(self) -> list[JobResult]:
        """Run all jobs that are due."""
        due = self.get_due_jobs()
        if not due:
            return []

        results = []
        for job in due:
            logger.info(f"Running scheduled job: {job.name}")
            result = await self.run_job(job)
            if result:
                results.append(result)
        return results

    async def run_loop(self, check_interval: float = 60.0) -> None:
        """Main scheduler loop — checks for due jobs every N seconds."""
        self._running = True
        logger.info(f"Scheduler started with {len(self.jobs)} jobs")
        while self._running:
            try:
                results = await self.run_due_jobs()
                for r in results:
                    logger.info(f"Job {r.job_name}: {r.decision.outcome} ({r.duration:.1f}s)")
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
            await asyncio.sleep(check_interval)

    def stop(self) -> None:
        self._running = False
