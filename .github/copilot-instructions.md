# Copilot Instructions — UE5 Agent (Starter)

## Purpose 🎯
This document gives an AI coding agent the immediate, actionable knowledge to be productive in this Unreal Engine 5 (UE5) “agent” repository: how the project is organized, which files to inspect first, important build/test/debug commands on Windows, and common code patterns to follow.

---

## Where to look first 🔎
- `*.uproject` — project entry; determines plugins and modules loaded.
- `Source/` — main C++ modules. Look for `*.Build.cs`, `Private/`, `Public/` subfolders.
- `Plugins/` — engine plugins (may contain runtime agents or editor integrations).
- `Content/` — assets and Blueprints used by agents.
- `Config/Default*.ini` — runtime configuration, server endpoints, plugin toggles.
- `Build/`, `Scripts/` or `CI/` — platform-specific build and CI steps.

Tip: use repository-wide searches for `IMPLEMENT_MODULE`, `MODULE_API`, `UCLASS`, `UFUNCTION`, and `RunUAT` to discover modules and automation.

---

## Big-picture architecture hints 🧩
- Agents are usually implemented as either:
  - **Editor plugin** (in `Plugins/`) that exposes tooling to the Editor, or
  - **Game/runtime module** (under `Source/<ModuleName>/`) that runs in packaged builds or dedicated servers.
- Key integration points: module startup (`StartupModule`), UObject-derived classes (`U*`), and Actors (`A*`) for in-world logic. Look for `IModuleInterface` implementations.

---

## Build & run (Windows examples) 🔧
- Regenerate project files: `Engine/GenerateProjectFiles.bat -project="<path>\Project.uproject"`
- Build in Visual Studio (preferred) or run: `Build.bat -Target="UE5" -Project="<path>\Project.uproject" -TargetPlatform=Win64 -Configuration=Development`
- Run Editor with project: `"<UE_ENGINE_PATH>\Engine\Binaries\Win64\UnrealEditor.exe" "<repo>\Project.uproject" -log`
- Package / Cook / Build: use `RunUAT.bat BuildCookRun -project="<path>\Project.uproject" -noP4 -platform=Win64 -clientconfig=Shipping`

Note: replace `<UE_ENGINE_PATH>` with the local Unreal installation path.

---

## Tests & dev environment 🧪
- Install developer dependencies locally (recommended in a virtualenv):

```powershell
python -m pip install --upgrade pip
pip install -r dev-requirements.txt
```

- Run tests: `pytest -q` (CI is configured in `.github/workflows/ci.yml`).
- Important: The agent uses `pydantic` for parameter validation when available; tests may run with a fallback validator if `pydantic` is not installed.

### Skill metadata & validation 🔧
- Each skill should include a `tool_def.json` describing the tools and parameter schemas (JSON Schema style). Example: `skills/ue5_medieval_builder/tool_def.json`.
- `SkillRegistry` will load `tool_def.json` and use `pydantic` (if available) to validate arguments coming back from the LLM before invoking the tool. If `pydantic` is not installed, a basic fallback validator is used.

- Configure your LLM credentials in environment variables (PowerShell example):

```powershell
$env:DEEPSEEK_API_KEY = "sk-..."
$env:DEEPSEEK_API_URL = "https://api.deepseek.com"
```

Do NOT commit API keys to the repo. Use local environment variables or a secrets manager.

---

## Tests & automation ✅
- Look for Automation Tests (C++ `IMPLEMENT_SIMPLE_AUTOMATION_TEST`) under `Source/` — run via the Editor's Test Framework or command-line with `-ExecCmds="Automation RunTests <TestName>; Quit"`.
- Find commandlets (`UCommandlet`) used for headless tasks (build/cook/asset processing).

---

## Debugging & logging 🔍
- Attach debugger to `UnrealEditor.exe` or a `ProjectName.exe` packaged server.
- Standard logging uses `UE_LOG(LogCategory, Log, TEXT("..."))`; search for `DEFINE_LOG_CATEGORY` to find categories.
- For runtime issues, consult `Saved/Logs/<Project>-*.log` and `Saved/Crashes/`.

---

## Project-specific conventions to look for 🧭
- C++ layout: `Source/<ModuleName>/Public` (API) vs `Private` (impl).
- Build config: `*.Build.cs` sets third-party dependencies and module dependencies.
- Naming: `U*` = UObject, `A*` = Actor, `F*` = plain structs, `I*` = interfaces.
- Reflection macros: prefer `UPROPERTY` for serialized/stateful fields and `UFUNCTION` for Blueprint-exposed APIs.

---

## Integration & external deps 🌐
- Check `Config/DefaultEngine.ini` or plugin `Config` for external endpoints (gRPC, REST, sockets). If present, look for initialization in module startup.
- Native 3rd-party libs: look in `ThirdParty/` folders and `*.Build.cs` referencing them.

---

## CI and platform notes ⚙️
- UE builds require Windows runners with UE installed or cached engine artifacts. Cache `DerivedDataCache`, `Binaries`, and installed Engine when possible.
- If `CI/` or `github/workflows` exist, follow their steps for build matrices and specific runner setup.

---

## How AI agents should act — immediate checklist ✔️
1. If `.github/copilot-instructions.md` exists, merge while preserving existing content. (This is a starter file.)
2. Search for `*.uproject`, `Source/`, `Plugins/`, `Config/Default*.ini` to map modules & plugins.
3. Identify module entry points: `IMPLEMENT_MODULE`, `StartupModule`, `ShutdownModule`.
4. Run local builds via `GenerateProjectFiles.bat` + Visual Studio; if failing, capture logs from `Saved/Logs`.
5. Locate tests (`Automation` macros) and run them via Editor `-ExecCmds`.
6. When proposing changes, include exact file paths, code snippets, and a one-line test plan.

---

## Examples (search queries to run immediately) 🔎
- `grep -R "IMPLEMENT_MODULE" -n` — find module implementations
- `grep -R "UCLASS\(|UFUNCTION\(|UPROPERTY\(" -n` — find reflected classes
- `rg "RunUAT|GenerateProjectFiles|BuildCookRun" -n` — find build scripts

---

> If anything above is missing or specific to this repo, tell me which files exist and I will update this file to reflect exact commands and patterns.

---

Please review this starter and tell me which parts to expand or any repo-specific commands and files to include. ✨
