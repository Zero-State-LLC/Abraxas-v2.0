from __future__ import annotations

from pathlib import Path


def _resolve_package_dir() -> Path:
    repo_root = Path(__file__).resolve().parent
    for candidate_name in ("scripts", "Scripts"):
        candidate = repo_root / candidate_name
        if (candidate / "__init__.py").exists():
            return candidate
    raise ModuleNotFoundError("No scripts package directory found")


_PACKAGE_DIR = _resolve_package_dir()
_INIT_PATH = _PACKAGE_DIR / "__init__.py"

__file__ = str(_INIT_PATH)
__path__ = [str(_PACKAGE_DIR)]
__package__ = __name__

if __spec__ is not None:
    __spec__.submodule_search_locations = [str(_PACKAGE_DIR)]

exec(compile(_INIT_PATH.read_text(encoding="utf-8"), __file__, "exec"), globals())
