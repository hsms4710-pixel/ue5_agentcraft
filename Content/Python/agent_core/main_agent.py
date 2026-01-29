import json
import re
import os
import unreal
from agent_core.skill_loader import SkillRegistry
from agent_core.llm import DeepseekClient

class UnrealAgent:
    def __init__(self):
        # 获取 skills 文件夹的绝对路径
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        skills_path = os.path.join(current_dir, "skills")

        # 加载所有技能
        self.registry = SkillRegistry(skills_path)

        # 初始化 LLM 客户端（需要环境变量 DEEPSEEK_API_KEY）
        try:
            self.llm = DeepseekClient()
            unreal.log("✅ Deepseek LLM client initialized")
        except Exception as e:
            self.llm = None
            unreal.log_error(f"⚠️ LLM 客户端未初始化: {e}")

    def run(self, user_input):
        unreal.log(f"🧠 Agent 收到指令: {user_input}")

        # 1. 构建 System Prompt
        system_prompt = "你是 UE5 助手。请根据以下工具定义，输出 JSON 指令。\n\n"
        system_prompt += "\n".join(self.registry.prompts)

        # 2. 调用 LLM（优先使用 Deepseek，失败则回退到本地 Mock）
        try:
            if hasattr(self, 'llm') and self.llm:
                response = self.llm.generate(system_prompt, user_input)
            else:
                response = self._mock_llm_inference(user_input)
        except Exception as e:
            unreal.log_error(f"⚠️ LLM 请求失败: {e}")
            response = self._mock_llm_inference(user_input)

        # 3. 解析并执行
        self._execute_tool_call(response)

    def _mock_llm_inference(self, user_input):
        """模拟大模型根据 README 里的定义返回 JSON"""
        if "铁匠铺" in user_input or "blacksmith" in user_input:
            return """
            ```json
            {
                "tool": "spawn_medieval_building",
                "args": {
                    "building_type": "blacksmith",
                    "location": [0, 0, 0],
                    "rotation_yaw": 90
                }
            }
            ```
            """
        return "无法理解指令"

    def _execute_tool_call(self, llm_response):
        # 解析 JSON
        match = re.search(r"```json\n(.*?)\n```", llm_response, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            tool_name = data["tool"]
            args = data["args"]

            # 动态调用
            if tool_name in self.registry.skills:
                unreal.log(f"🔨 执行工具: {tool_name}")
                func = self.registry.skills[tool_name]
                # 参数校验（基于 tool_def.json -> pydantic 优先）
                try:
                    self.registry.validate_tool_call(tool_name, args)
                except ValueError as ve:
                    unreal.log_error(f"❌ 参数校验失败: {ve}")
                    return

                result = func(**args)  # 传入参数
                unreal.log(result)
            else:
                unreal.log_error(f"❌ 未找到工具: {tool_name}")
