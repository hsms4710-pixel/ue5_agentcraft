import os
import importlib.util
import sys
import json

class SkillRegistry:
    def __init__(self, skills_root_path):
        self.skills = {}  # 存储 { "spawn_medieval_building": skill_instance.method }
        self.prompts = []  # 存储所有的 README 内容
        self.tool_defs = {}  # 存储工具的结构化定义 (来自 tool_def.json)
        self._load_skills(skills_root_path)

    def validate_tool_call(self, tool_name: str, args: dict):
        """Validate args for a given tool using tool_defs. Raises ValueError on invalid."""
        if tool_name not in self.tool_defs:
            return True

        schema = self.tool_defs[tool_name].get("parameters")
        if not schema:
            return True

        # Prefer pydantic for validation
        try:
            from pydantic import BaseModel, ValidationError, create_model
            from typing import List, Optional

            props = schema.get("properties", {})
            required = set(schema.get("required", []))
            fields = {}
            for name, ps in props.items():
                ptype = ps.get("type")
                if ptype == "string":
                    python_type = (str, ... if name in required else None)
                elif ptype == "number":
                    python_type = (float, ... if name in required else None)
                elif ptype == "integer":
                    python_type = (int, ... if name in required else None)
                elif ptype == "array":
                    python_type = (list, ... if name in required else None)
                elif ptype == "boolean":
                    python_type = (bool, ... if name in required else None)
                else:
                    python_type = (object, ... if name in required else None)

                # create_model expects keyword as name=(type, default)
                default = ... if name in required else None
                fields[name] = (python_type[0], default)

            Model = create_model(f"Tool_{tool_name}_Model", **fields)
            Model(**args)
            return True
        except ImportError:
            # Fallback lightweight validation
            props = schema.get("properties", {})
            required = schema.get("required", [])
            missing = [r for r in required if r not in args]
            if missing:
                raise ValueError(f"Missing required params: {missing}")

            # Basic type checks
            for name, ps in props.items():
                if name in args and args[name] is not None:
                    ptype = ps.get("type")
                    val = args[name]
                    if ptype == "array":
                        if not isinstance(val, list):
                            raise ValueError(f"Param {name} must be a list")
                        min_items = ps.get("minItems")
                        max_items = ps.get("maxItems")
                        if min_items is not None and len(val) < min_items:
                            raise ValueError(f"Param {name} must have at least {min_items} items")
                        if max_items is not None and len(val) > max_items:
                            raise ValueError(f"Param {name} must have at most {max_items} items")
                    if ptype == "number":
                        if not isinstance(val, (int, float)):
                            raise ValueError(f"Param {name} must be a number")
                    if ptype == "string":
                        if not isinstance(val, str):
                            raise ValueError(f"Param {name} must be a string")
            return True
        except Exception as e:
            # Re-raise as ValueError for consistent handling
            raise ValueError(str(e))

    def _load_skills(self, root_path):
        if not os.path.exists(root_path):
            print(f"⚠️ Skills 目录不存在: {root_path}")
            return

        # 遍历 skills 目录下的所有子文件夹
        for folder_name in os.listdir(root_path):
            folder_path = os.path.join(root_path, folder_name)
            if os.path.isdir(folder_path):
                self._register_single_skill(folder_path, folder_name)

    def _register_single_skill(self, folder_path, skill_name):
        # 1. 读取 README.md 作为 Prompt
        readme_path = os.path.join(folder_path, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                self.prompts.append(f"--- Skill: {skill_name} ---\n{f.read()}\n")

        # 2. 读取结构化工具定义 tool_def.json（可选）
        tool_def_path = os.path.join(folder_path, "tool_def.json")
        if os.path.exists(tool_def_path):
            try:
                with open(tool_def_path, 'r', encoding='utf-8') as f:
                    td = f.read()
                    # 保留原文作为 prompt 的一部分
                    self.prompts.append(f"--- ToolDef: {skill_name} ---\n{td}\n")
                    data = json.loads(td)
                    tools = data.get('tools', [])
                    for t in tools:
                        tname = t.get('name')
                        if tname:
                            self.tool_defs[tname] = t
                            print(f"🔧 已加载工具定义: {tname}")
            except Exception as e:
                print(f"⚠️ 解析 tool_def.json 失败: {e}")

        # 3. 动态加载 skill.py
        script_path = os.path.join(folder_path, "skill.py")
        if os.path.exists(script_path):
            # Python 动态导入黑魔法
            spec = importlib.util.spec_from_file_location(f"skills.{skill_name}", script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"skills.{skill_name}"] = module
            spec.loader.exec_module(module)

            # 实例化 Skill 类
            if hasattr(module, "Skill"):
                skill_instance = module.Skill()

                # 4. 自动注册所有公开方法为工具
                # 只要方法名不以 _ 开头，就被视为可被 AI 调用的 Tool
                for attr_name in dir(skill_instance):
                    if not attr_name.startswith("_") and callable(getattr(skill_instance, attr_name)):
                        self.skills[attr_name] = getattr(skill_instance, attr_name)
                        print(f"✅ 已注册能力: {attr_name}")
