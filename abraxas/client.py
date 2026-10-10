"""Supported Python product client (library API)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.application.advisory_spine import AdvisorySpineRequest, run_advisory_spine
from core.application.status import build_status_snapshot
from core.governance.activation_policy import ActivationLane
from core.runtime_context import RuntimeContext
from core.services.validation_service import validate as validation_validate
from core.settings import RuntimeSettings, load_runtime_settings


class AbraxasClient:
    """Stable library facade over the supported advisory spine.

    Does not grant EXTERNAL_PRODUCTION authority. Disk writes are opt-in via
    callers; this client remains pure by default.
    """

    def __init__(
        self,
        *,
        settings: RuntimeSettings | None = None,
        context: RuntimeContext | None = None,
        repo_root: Path | None = None,
        default_lane: ActivationLane | str | None = None,
    ) -> None:
        if context is not None and settings is not None:
            raise ValueError("pass context or settings, not both")
        if context is not None:
            self.context = context
            self.settings = context.settings
        elif settings is not None:
            self.settings = settings
            self.context = RuntimeContext.build(settings)
        else:
            overrides: dict[str, Any] = {}
            if repo_root is not None:
                overrides["repo_root"] = Path(repo_root).resolve()
            if default_lane is not None:
                overrides["default_activation_lane"] = default_lane
            self.settings = load_runtime_settings(**overrides)
            self.context = RuntimeContext.build(self.settings)
        self.repo_root = Path(self.settings.repo_root).resolve()
        self.default_lane = ActivationLane(self.settings.default_activation_lane)

    def analyze(
        self,
        *,
        run_id: str,
        input_payload: Mapping[str, Any] | None = None,
        schema_ref: str | None = None,
        alembic_task: Mapping[str, Any] | None = None,
        oracle_candidate: Mapping[str, Any] | None = None,
        enable_alembic: bool = True,
        alembic_mode: str = "advisory",
        activation_lane: ActivationLane | str | None = None,
    ) -> dict[str, Any]:
        request = AdvisorySpineRequest(
            run_id=run_id,
            activation_lane=ActivationLane(activation_lane or self.default_lane),
            input_payload=dict(input_payload or {}),
            schema_ref=schema_ref,
            alembic_task=dict(alembic_task) if alembic_task is not None else None,
            oracle_candidate=(
                dict(oracle_candidate) if oracle_candidate is not None else None
            ),
            enable_alembic=enable_alembic,
            alembic_mode=alembic_mode,  # type: ignore[arg-type]
        )
        return run_advisory_spine(request, repo_root=self.repo_root)

    def validate(
        self,
        *,
        schema_ref: str,
        payload: Any,
        execution_id: str = "abraxas-client-validate",
    ) -> dict[str, Any]:
        return validation_validate(
            {
                "schema_version": "ValidationServiceRequest.v1",
                "service_id": "validation_service",
                "execution_id": execution_id,
                "schema_ref": schema_ref,
                "payload": payload,
            },
            repo_root=self.repo_root,
        )

    def status(self) -> dict[str, Any]:
        return build_status_snapshot(self.repo_root, settings=self.settings)

    def replay(
        self,
        receipt: Mapping[str, Any],
        *,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Replay a prior advisory-spine or Alembic-oriented receipt."""
        payload = dict(receipt)
        task = None
        if isinstance(payload.get("alembic"), dict) and payload["alembic"].get("task"):
            task = payload["alembic"]["task"]
        elif isinstance(payload.get("task"), dict):
            task = payload["task"]
        elif (
            isinstance(payload.get("replay_manifest"), dict)
            and payload["replay_manifest"].get("task")
        ):
            task = payload["replay_manifest"]["task"]

        if task is None:
            return {
                "status": "ERROR",
                "error_class": "REPLAY_INPUT_INVALID",
                "message": "Receipt missing alembic.task / task / replay_manifest.task",
            }

        replay_run_id = run_id or str(
            task.get("run_id") or payload.get("run_id") or "replay"
        )
        return self.analyze(
            run_id=f"replay:{replay_run_id}",
            input_payload={"replay": True, "source_run_id": replay_run_id},
            alembic_task=task,
            enable_alembic=True,
            alembic_mode="advisory",
        )
