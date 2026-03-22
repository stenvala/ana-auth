"""Tests for mcc_config.py template variable resolution."""

# Import from project root
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from mcc_config import _resolve_templates


class TestResolveTemplates:
    def test_simple_substitution(self) -> None:
        config = {"BASE": "/home/user", "LOG": "{{BASE}}/logs"}
        result = _resolve_templates(config)
        assert result["LOG"] == "/home/user/logs"

    def test_no_template_variables(self) -> None:
        config = {"HOST": "localhost", "PORT": "5432"}
        result = _resolve_templates(config)
        assert result == {"HOST": "localhost", "PORT": "5432"}

    def test_nested_variable_substitution(self) -> None:
        config = {
            "ROOT": "/opt",
            "BASE": "{{ROOT}}/app",
            "LOGS": "{{BASE}}/logs",
        }
        result = _resolve_templates(config)
        assert result["ROOT"] == "/opt"
        assert result["BASE"] == "/opt/app"
        assert result["LOGS"] == "/opt/app/logs"

    def test_cycle_detection(self) -> None:
        config = {"A": "{{B}}", "B": "{{A}}"}
        with pytest.raises(ValueError, match="Cycle detected"):
            _resolve_templates(config)

    def test_self_reference_cycle(self) -> None:
        config = {"A": "{{A}}"}
        with pytest.raises(ValueError, match="Cycle detected"):
            _resolve_templates(config)

    def test_three_way_cycle(self) -> None:
        config = {"A": "{{B}}", "B": "{{C}}", "C": "{{A}}"}
        with pytest.raises(ValueError, match="Cycle detected"):
            _resolve_templates(config)

    def test_undefined_variable_left_as_is(self) -> None:
        config = {"A": "{{UNDEFINED}}"}
        result = _resolve_templates(config)
        assert result["A"] == "{{UNDEFINED}}"

    def test_multiple_variables_in_one_value(self) -> None:
        config = {
            "HOST": "localhost",
            "PORT": "5432",
            "URL": "{{HOST}}:{{PORT}}",
        }
        result = _resolve_templates(config)
        assert result["URL"] == "localhost:5432"

    def test_value_without_templates_unchanged(self) -> None:
        config = {"PLAIN": "no templates here"}
        result = _resolve_templates(config)
        assert result["PLAIN"] == "no templates here"
