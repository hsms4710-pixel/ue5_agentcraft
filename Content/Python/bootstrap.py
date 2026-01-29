import sys
import os
import importlib

# Ensure Content/Python is on sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Reload modules for convenience in the Editor
import agent_core.skill_manager
importlib.reload(agent_core.skill_manager)

from agent_core.skill_manager import SkillManager

# Demo using SkillManager (RAG retrieval + execute)
def start():
    skills_path = os.path.join(current_dir, "skills")
    manager = SkillManager(skills_path)

    # Example query — RAG will narrow down relevant tools
    tools = manager.retrieve_tools("请在原点放一个铁匠铺", top_k=3)
    print("Relevant tools:", [t.get('name') for t in tools])

    # Example execute (calls UEBridge which runs in mock mode if not in Editor)
    res = manager.execute_tool("spawn_medieval_building", building_type="blacksmith", location=[0,0,0], rotation_yaw=90)
    print("Execute result:", res)

if __name__ == "__main__":
    start()
