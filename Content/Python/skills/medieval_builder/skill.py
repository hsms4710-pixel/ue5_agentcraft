from typing import Any
from agent_core.base_tool import BaseTool
from agent_core.ue_bridge import UEBridge

class MedievalBuilderSkill(BaseTool):
    name = "spawn_medieval_building"
    description = "Spawn a medieval building at a location"

    def run(self, building_type: str, location: list, rotation_yaw: float = 0) -> Any:
        # 1. Lookup
        if building_type not in self.config:
            return {
                "status": "error",
                "msg": f"未知建筑类型 '{building_type}'. 可用类型: {list(self.config.keys())}"
            }

        asset_info = self.config[building_type]
        asset_path = asset_info.get("asset_path", "")

        # 2. Use the UE bridge
        result = UEBridge.safe_spawn_actor(
            asset_path=asset_path,
            location=location,
            rotation=[0, rotation_yaw, 0]
        )

        return result
