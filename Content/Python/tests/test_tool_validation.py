import os
import sys
import types
import pytest

# Ensure Content/Python is on sys.path for tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent_core.skill_loader import SkillRegistry


def test_tool_def_loaded_and_validation_success():
    base = os.path.dirname(os.path.dirname(__file__))
    skills_path = os.path.join(base, "skills")
    registry = SkillRegistry(skills_path)

    assert "spawn_medieval_building" in registry.tool_defs

    good_args = {
        "building_type": "blacksmith",
        "location": [0, 0, 0],
        "rotation_yaw": 90,
    }

    # Should not raise
    assert registry.validate_tool_call("spawn_medieval_building", good_args) is True


def test_tool_validation_fails_on_bad_location():
    base = os.path.dirname(os.path.dirname(__file__))
    skills_path = os.path.join(base, "skills")
    registry = SkillRegistry(skills_path)

    bad_args = {
        "building_type": "blacksmith",
        "location": [0, 0],  # too short
    }

    with pytest.raises(ValueError):
        registry.validate_tool_call("spawn_medieval_building", bad_args)
