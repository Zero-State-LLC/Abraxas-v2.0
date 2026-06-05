from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_script_runner(repo_root: Path, relative_path: str, module_name: str) -> ModuleType:
    runner_path = repo_root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, runner_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load script runner from {runner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
