"""Tests for decision templates."""

import pytest

from swarm_agency.templates import (
    DecisionTemplate,
    TEMPLATES,
    create_request,
    list_templates,
)
from swarm_agency.types import AgencyRequest


class TestTemplateDefinitions:
    def test_all_five_templates_exist(self):
        expected = {"hire", "pricing", "launch", "vendor", "pivot"}
        assert set(TEMPLATES.keys()) == expected

    def test_each_template_has_required_fields(self):
        for name, tmpl in TEMPLATES.items():
            assert tmpl.name, f"{name} missing name"
            assert tmpl.question_format, f"{name} missing question_format"
            assert tmpl.departments, f"{name} missing departments"
            assert tmpl.required_fields, f"{name} missing required_fields"

    def test_list_templates(self):
        names = list_templates()
        assert len(names) == 5
        assert "hire" in names


class TestCreateRequest:
    def test_hire_template(self):
        req = create_request("hire", candidate="Jane", role="CTO")
        assert isinstance(req, AgencyRequest)
        assert "Jane" in req.question
        assert "CTO" in req.question
        assert req.metadata["template"] == "hire"

    def test_pricing_template(self):
        req = create_request(
            "pricing", product="Widget", current_price="$10", new_price="$15"
        )
        assert "Widget" in req.question
        assert "$10" in req.question
        assert "$15" in req.question

    def test_launch_template(self):
        req = create_request("launch", product="AppX", market="Europe")
        assert "AppX" in req.question
        assert "Europe" in req.question

    def test_vendor_template(self):
        req = create_request("vendor", vendor="AWS", service="cloud hosting")
        assert "AWS" in req.question
        assert "cloud hosting" in req.question

    def test_pivot_template(self):
        req = create_request(
            "pivot", current_direction="B2C", new_direction="B2B"
        )
        assert "B2C" in req.question
        assert "B2B" in req.question

    def test_unknown_template_raises(self):
        with pytest.raises(ValueError, match="Unknown template"):
            create_request("nonexistent")

    def test_missing_required_field_raises(self):
        with pytest.raises(ValueError, match="requires fields"):
            create_request("hire", candidate="Jane")  # missing 'role'

    def test_custom_context(self):
        req = create_request(
            "hire", candidate="Bob", role="Engineer", context="Urgently needed"
        )
        assert req.context == "Urgently needed"

    def test_default_context_used(self):
        req = create_request("hire", candidate="Bob", role="Engineer")
        assert req.context  # should use template default

    def test_custom_request_id(self):
        req = create_request(
            "hire", request_id="custom-123", candidate="X", role="Y"
        )
        assert req.request_id == "custom-123"

    def test_auto_generated_request_id(self):
        req = create_request("hire", candidate="X", role="Y")
        assert req.request_id.startswith("tmpl-")

    def test_template_fields_in_metadata(self):
        req = create_request("hire", candidate="Jane", role="CTO")
        assert req.metadata["template_fields"]["candidate"] == "Jane"
        assert req.metadata["template_fields"]["role"] == "CTO"
