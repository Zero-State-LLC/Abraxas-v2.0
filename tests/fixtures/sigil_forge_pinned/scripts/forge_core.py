"""Pinned replay of Sigil-Forge forge_core for Abraxas contract tests.

Not the engine. Returns the outputs recorded in ../forge_core_outputs.v1.json
(see ../PROVENANCE.md) and refuses any intent or config it has no record for,
so a test can never pass on invented primitives. Abraxas-authored; contains
no Sigil-Forge code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

_RECORD = json.loads(
    (Path(__file__).resolve().parents[1] / "forge_core_outputs.v1.json").read_text(
        encoding="utf-8"
    )
)
_BY_NORMALIZED = {row["normalized"]: row for row in _RECORD["outputs"]}
PINNED_COMMIT = _RECORD["source_commit"]


@dataclass(frozen=True)
class ForgeConfig:
    mode: str = "creative"
    spare_mode: str = "letter_monogram"


def compute_forge(
    normalized: str, config: ForgeConfig | None = None
) -> SimpleNamespace:
    cfg = config or ForgeConfig()
    if {"mode": cfg.mode, "spare_mode": cfg.spare_mode} != _RECORD["config"]:
        raise LookupError(f"pinned replay has no record for config {cfg!r}")
    row = _BY_NORMALIZED.get(normalized)
    if row is None:
        raise LookupError(
            "pinned replay has no record for this intent; regenerate the fixture"
        )
    return SimpleNamespace(
        normalized=normalized,
        intent_digest=row["intent_digest"],
        spare_letters=row["spare_letters"],
        square_name=row["square_name"],
        square_order=row["square_order"],
    )
