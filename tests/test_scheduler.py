"""Tests for the agent scheduler."""

import json
import pytest
from swarm_agency.scheduler import AgentScheduler, ScheduledJob, DEFAULT_JOBS


@pytest.fixture
def scheduler(tmp_path):
    jobs_file = str(tmp_path / "jobs.json")
    return AgentScheduler(agency=None, jobs_file=jobs_file)


class TestScheduler:
    def test_default_jobs_loaded(self, scheduler):
        jobs = scheduler.list_jobs()
        assert len(jobs) >= 4
        names = [j.name for j in jobs]
        assert "Daily Business Health Check" in names
        assert "Devil's Advocate Challenge" in names

    def test_add_job(self, scheduler):
        job = ScheduledJob(
            job_id="test-job", name="Test", description="Test job",
            department="Strategy", question_template="Test?",
            context_template="", schedule="daily", interval_hours=24,
        )
        scheduler.add_job(job)
        assert "test-job" in scheduler.jobs

    def test_remove_job(self, scheduler):
        scheduler.remove_job("daily-health-check")
        assert "daily-health-check" not in scheduler.jobs

    def test_enable_disable(self, scheduler):
        scheduler.disable_job("daily-health-check")
        assert scheduler.jobs["daily-health-check"].enabled is False
        scheduler.enable_job("daily-health-check")
        assert scheduler.jobs["daily-health-check"].enabled is True

    def test_due_jobs(self, scheduler):
        # All jobs should be due (last_run=0)
        due = scheduler.get_due_jobs()
        assert len(due) >= 4

    def test_persistence(self, tmp_path):
        jobs_file = str(tmp_path / "persist.json")
        s1 = AgentScheduler(agency=None, jobs_file=jobs_file)
        s1.add_job(ScheduledJob(
            job_id="custom", name="Custom", description="",
            department=None, question_template="?", context_template="",
            schedule="daily", interval_hours=24,
        ))

        s2 = AgentScheduler(agency=None, jobs_file=jobs_file)
        assert "custom" in s2.jobs
