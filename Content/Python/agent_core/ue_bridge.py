"""UE5 bridge — safe interactions with the Unreal Editor.

All code that interacts with `unreal` should go through this module so the rest
of the system can run safely in a non-UE environment (mock mode).
"""

try:
    import unreal  # type: ignore
    _HAS_UNREAL = True
except Exception:
    _HAS_UNREAL = False
    unreal = None
    print("⚠️ 运行在模拟模式 (无 UE5 环境)")


class UEBridge:
    @staticmethod
    def safe_spawn_actor(asset_path: str, location: list, rotation: list = None):
        """Safely spawn an actor based on an asset path.

        Returns a dict with a status and message. In a non-UE Python environment
        this returns a mock success message instead of raising.
        """
        rotation = rotation or [0, 0, 0]

        if not _HAS_UNREAL:
            return {"status": "mock_success", "msg": f"Mock Spawn {asset_path} at {location}"}

        # 1. Asset existence check
        if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            return {
                "status": "error",
                "code": "ASSET_MISSING",
                "msg": f"在项目中找不到资产: {asset_path}。请检查 config.json 配置。"
            }

        try:
            # Convert to unreal types
            vec_loc = unreal.Vector(location[0], location[1], location[2])
            rot_rot = unreal.Rotator(rotation[1], rotation[2], rotation[0])

            actor_class = unreal.StaticMeshActor
            actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, vec_loc, rot_rot)

            # Load mesh and set it
            mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
            # try common component access patterns
            if hasattr(actor, 'static_mesh_component') and actor.static_mesh_component:
                actor.static_mesh_component.set_static_mesh(mesh)
            else:
                comp = actor.get_component_by_class(unreal.StaticMeshComponent)
                if comp:
                    comp.set_static_mesh(mesh)

            return {
                "status": "success",
                "actor_label": actor.get_actor_label(),
                "location": location
            }
        except Exception as e:
            return {"status": "error", "msg": str(e)}
