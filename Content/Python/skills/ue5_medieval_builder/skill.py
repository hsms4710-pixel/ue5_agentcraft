import unreal
import json
import os

class Skill:
    """
    每个 Skill 文件夹下必须包含这个类，作为入口。
    """
    def __init__(self):
        # 动态加载同目录下的 JSON 配置
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, "assets_config.json"), 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        # 使用模块方式访问 Editor API（更可靠）
        self.editor_level_lib = unreal.EditorLevelLibrary
        self.editor_asset_lib = unreal.EditorAssetLibrary

    def spawn_medieval_building(self, building_type, location, rotation_yaw=0):
        """
        对应 README.md 中的工具名称
        """
        # 1. 查表获取路径
        if building_type not in self.config["catalog"]:
            return f"Error: Unknown type '{building_type}'"

        asset_info = self.config["catalog"][building_type]
        path = asset_info["asset_path"]

        # 2. 检查资产
        if not self.editor_asset_lib.does_asset_exist(path):
            return f"Error: Asset not found at {path}"

        # 3. 准备数据 (利用 unreal API)
        u_loc = unreal.Vector(location[0], location[1], location[2] + asset_info.get("offset_z", 0))
        u_rot = unreal.Rotator(0, rotation_yaw, 0)

        # 4. 生成 Actor
        actor = self.editor_level_lib.spawn_actor_from_class(unreal.StaticMeshActor, u_loc, u_rot)
        if not actor:
            return "Error: Failed to spawn actor"

        # 5. 加载并设置模型
        mesh = self.editor_asset_lib.load_asset(path)
        if not mesh:
            return f"Error: Failed to load mesh at {path}"

        # 尝试设置静态网格组件
        try:
            # 有时属性名为 static_mesh_component 或 StaticMeshComponent
            if hasattr(actor, 'static_mesh_component') and actor.static_mesh_component:
                actor.static_mesh_component.set_static_mesh(mesh)
            else:
                # 尝试通过组件类获取
                comp = actor.get_component_by_class(unreal.StaticMeshComponent)
                if comp:
                    comp.set_static_mesh(mesh)
        except Exception as e:
            return f"Error: Failed to set mesh: {e}"

        actor.set_actor_label(f"Medieval_{building_type}")

        return f"Success: Spawned {building_type} at {location}"
