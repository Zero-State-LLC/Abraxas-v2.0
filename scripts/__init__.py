from __future__ import annotations

from importlib import import_module

_scripts = import_module("scripts")
__path__ = list(getattr(_scripts, "__path__", []))
__all__ = getattr(_scripts, "__all__", [])
