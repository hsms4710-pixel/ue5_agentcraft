import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agent_core.skill_manager import SkillManager


def test_loads_medieval_skill_and_executes():
    base = os.path.dirname(os.path.dirname(__file__))
    skills_path = os.path.join(base, 'skills')

    sm = SkillManager(skills_path)

    # RAG should find the spawn tool
    tools = sm.retrieve_tools('建一个房子', top_k=3)
    assert any(t.get('name') == 'spawn_medieval_building' for t in tools)

    # Execution in mock mode should return mock_success
    res = sm.execute_tool('spawn_medieval_building', building_type='blacksmith', location=[0,0,0])
    assert isinstance(res, dict)
    assert res.get('status') in ('mock_success', 'success')
