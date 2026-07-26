"""Alembic architecture adapters."""

from __future__ import annotations

from core.alembic.adapters.deterministic_tool import DeterministicToolAdapter
from core.alembic.adapters.graph import GraphMemeticAdapter
from core.alembic.adapters.statistical import StatisticalCalibratorAdapter
from core.alembic.adapters.stubs import (
    GenerativeStubAdapter,
    OperatorReviewAdapter,
    SpikingNeuromorphicStubAdapter,
    StateSpaceStubAdapter,
)
from core.alembic.adapters.symbolic import SymbolicVerifierAdapter

DEFAULT_ADAPTERS: tuple[object, ...] = (
    SymbolicVerifierAdapter(),
    DeterministicToolAdapter(),
    StatisticalCalibratorAdapter(),
    GraphMemeticAdapter(),
    StateSpaceStubAdapter(),
    GenerativeStubAdapter(),
    SpikingNeuromorphicStubAdapter(),
    OperatorReviewAdapter(),
)

__all__ = [
    "DEFAULT_ADAPTERS",
    "DeterministicToolAdapter",
    "GenerativeStubAdapter",
    "GraphMemeticAdapter",
    "OperatorReviewAdapter",
    "SpikingNeuromorphicStubAdapter",
    "StateSpaceStubAdapter",
    "StatisticalCalibratorAdapter",
    "SymbolicVerifierAdapter",
]
