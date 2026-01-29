import sys
import os
import importlib

# 确保当前路径在 sys.path 中 (防止导入错误)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 强制重载模块 (方便你修改代码后不用重启 UE5)
import agent_core.skill_loader
import agent_core.main_agent
importlib.reload(agent_core.skill_loader)
importlib.reload(agent_core.main_agent)

from agent_core.main_agent import UnrealAgent

# 运行演示
def start():
    agent = UnrealAgent()
    # 发送指令
    agent.run("帮我在原点建一个朝东的铁匠铺")

if __name__ == "__main__":
    start()
