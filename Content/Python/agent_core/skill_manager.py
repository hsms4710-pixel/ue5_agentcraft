import os
import json
import importlib.util
from typing import List, Dict, Any

from agent_core.base_tool import BaseTool

class SkillManager:
    """Loads skills (BaseTool subclasses), exposes RAG-like retrieval and execution."""

    def __init__(self, skills_root: str):
        self.skills_root = skills_root
        self.registry: Dict[str, BaseTool] = {}
        self.definitions: List[Dict[str, Any]] = []
        self.index: List[Dict[str, Any]] = []  # simple keyword index

        self._load_all_skills()

    def _load_all_skills(self):
        for folder in os.listdir(self.skills_root):
            folder_path = os.path.join(self.skills_root, folder)
            if not os.path.isdir(folder_path):
                continue

            # load tool_def.json if present
            def_path = os.path.join(folder_path, "tool_def.json")
            if not os.path.exists(def_path):
                continue

            try:
                with open(def_path, 'r', encoding='utf-8') as f:
                    tool_def = json.load(f)
            except Exception as e:
                print(f"⚠️ 无法解析 {def_path}: {e}")
                continue

            # Dynamic import of skill implementation
            skill_py = os.path.join(folder_path, "skill.py")
            if not os.path.exists(skill_py):
                print(f"⚠️ 未找到实现: {skill_py}")
                continue

            spec = importlib.util.spec_from_file_location(f"skills.{folder}", skill_py)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Normalize tool_def: support {"tools": [...] } or single-tool top-level
            tools = []
            if isinstance(tool_def, dict) and "tools" in tool_def and isinstance(tool_def["tools"], list):
                tools = tool_def["tools"]
            else:
                # assume the file itself describes a single tool
                tools = [tool_def]

            # instantiate matching classes found in module
            for t in tools:
                tname = t.get('name')
                if not tname:
                    continue

                # Find a class in module that ends with 'Skill'
                cls = None
                for attr in dir(module):
                    if attr.endswith('Skill') and attr != 'BaseTool':
                        candidate = getattr(module, attr)
                        try:
                            instance = candidate(os.path.join(folder_path, 'config.json'))
                            if isinstance(instance, BaseTool):
                                cls = instance
                                break
                        except Exception as e:
                            print(f"⚠️ 无法实例化 {attr}: {e}")

                if cls is None:
                    print(f"⚠️ 在 {skill_py} 中未找到可用的 Skill 实现")
                    continue

                # register
                self.registry[tname] = cls
                self.definitions.append(t)
                self.index.append({
                    'name': tname,
                    'desc': t.get('description', ''),
                    'keywords': set(str(t.get('description', '')).split())
                })

                print(f"✅ Loaded Skill: {tname}")

    def retrieve_tools(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_words = set(query.split())
        scored = []
        for item in self.index:
            score = 0
            for w in query_words:
                if w in item['desc']:
                    score += 1
            scored.append((score, item['name']))
        scored.sort(key=lambda x: x[0], reverse=True)
        top_names = [t[1] for t in scored[:top_k]]
        return [d for d in self.definitions if d.get('name') in top_names]

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        if tool_name in self.registry:
            try:
                return self.registry[tool_name].run(**kwargs)
            except Exception as e:
                return {"status": "error", "msg": str(e)}
        return {"status": "error", "msg": f"Tool {tool_name} not found"}
