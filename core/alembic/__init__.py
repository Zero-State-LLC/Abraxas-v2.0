"""Alembic Spine — governed multi-architecture orchestration (advisory-only)."""

from __future__ import annotations

from core.alembic.config import RouterPolicy, default_router_policy, load_router_policy
from core.alembic.constants import FINAL_STATUS, SPINE_VERSION
from core.alembic.pipeline import execute_advisory, route_only
from core.alembic.registry import ArchitectureRegistry, default_registry

__all__ = [
    "FINAL_STATUS",
    "SPINE_VERSION",
    "ArchitectureRegistry",
    "RouterPolicy",
    "default_registry",
    "default_router_policy",
    "execute_advisory",
    "load_router_policy",
    "route_only",
]
