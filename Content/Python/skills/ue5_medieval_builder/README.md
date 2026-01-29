# Medieval Building Skill

此技能用于生成中世纪风格的建筑。

## Tool Definition

```json
{
  "name": "spawn_medieval_building",
  "description": "在指定位置生成中世纪建筑。支持类型：blacksmith, house_small, watchtower。",
  "parameters": {
    "building_type": {
      "type": "string",
      "description": "建筑类型，必须是 catalog 中的 key。"
    },
    "location": {
      "type": "list",
      "description": "[x, y, z] 坐标。"
    },
    "rotation_yaw": {
      "type": "number",
      "description": "Z轴旋转角度，默认0。"
    }
  }
}
```
