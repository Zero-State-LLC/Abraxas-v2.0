from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, model_validator

# TD Wave 1: pure builder — sole-writer scripts own out/ publication.
from core.file_cache import read_text_cached
from core.governance.authority import Authority


class MilestoneContinuityPacket(BaseModel):
    schema_version: Literal["MilestoneContinuityPacket.v1"] = "MilestoneContinuityPacket.v1"
    continuity_id: str
    required_scripts: list[str]
    missing_scripts: list[str]
    required_artifacts: list[str]
    missing_artifacts: list[str]
    required_routes: list[str]
    missing_routes: list[str]
    deterministic_hash: str
    authority: Authority = Authority()
    status: str

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "MilestoneContinuityPacket":
        self.authority.assert_locked()
        expected = sha256(
            "|".join(self.required_scripts + self.missing_scripts + self.required_artifacts + self.missing_artifacts + self.required_routes + self.missing_routes).encode()
        ).hexdigest()
        if self.deterministic_hash != expected:
            raise ValueError("deterministic continuity hash mismatch")
        return self


def validate_milestone_continuity() -> MilestoneContinuityPacket:
    required_scripts = [
        "scripts/run_registry.py", "scripts/run_doctrine_validator.py", "scripts/run_shadow_execution.py",
        "scripts/run_rune_replay.py", "scripts/run_yggdrasil_runtime.py", "scripts/run_graph_replay.py",
        "scripts/run_observability_pipeline.py", "scripts/run_lineage_validation.py", "scripts/run_state_engine.py", "scripts/run_state_replay.py",
    ]
    required_artifacts = [
        "out/registry/latest.json", "out/validation/latest.json", "out/projections/aal_viz.latest.json",
        "out/state/latest.json", "out/state_lineage/latest.json", "out/stabilization/latest.json", "out/state_replay/latest.json",
    ]
    required_routes = ["/health", "/registry", "/validation", "/projection"]

    exists_cache: dict[str, bool] = {}

    def exists(path: str) -> bool:
        if path not in exists_cache:
            exists_cache[path] = Path(path).exists()
        return exists_cache[path]

    def read_optional(path: str) -> str:
        return read_text_cached(path) if exists(path) else ""

    missing_scripts = [s for s in required_scripts if not exists(s)]
    missing_artifacts = [a for a in required_artifacts if not exists(a)]

    main_text = read_optional("apps/api/main.py")
    validation_text = read_optional("apps/api/routers/validation.py")
    health_text = read_optional("apps/api/routers/health.py")
    registry_text = read_optional("apps/api/routers/registry.py")
    route_blob = "\n".join([main_text, validation_text, health_text, registry_text])
    missing_routes = [r for r in required_routes if r not in route_blob]
    det = sha256("|".join(required_scripts + missing_scripts + required_artifacts + missing_artifacts + required_routes + missing_routes).encode()).hexdigest()
    status = "failed" if (missing_scripts or missing_artifacts or missing_routes) else "passed"
    return MilestoneContinuityPacket(
        continuity_id=f"continuity:{det[:12]}", required_scripts=required_scripts, missing_scripts=missing_scripts,
        required_artifacts=required_artifacts, missing_artifacts=missing_artifacts, required_routes=required_routes,
        missing_routes=missing_routes, deterministic_hash=det, status=status
    )
