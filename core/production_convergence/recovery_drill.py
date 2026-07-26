"""Production-convergence recovery drill (analyze → persist → replay)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from abraxas.client import AbraxasClient
from core.canonical.artifact_classification import ArtifactClass
from core.ports.clock import FixedClock
from core.runtime_context import RuntimeContext
from core.settings import load_runtime_settings


def run_recovery_drill(
    *,
    repo_root: Path,
    work_dir: Path,
    alembic_task: dict[str, Any],
    clock_instant: str = "2026-07-26T00:00:00Z",
    run_id: str = "convergence-recovery-drill",
) -> dict[str, Any]:
    """Execute a LOCAL_DEV recovery drill without mutating tracked out/ trees.

    Steps:
    1. Analyze with optional Alembic task under FixedClock context
    2. Persist advisory receipt via ArtifactStore
    3. Replay from persisted receipt
    4. Re-persist and assert classified hash stability for the receipt body
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    settings = load_runtime_settings(
        repo_root=repo_root,
        out_dir=work_dir / "out",
        default_activation_lane="LOCAL_DEV",
    )
    ctx = RuntimeContext.build(settings, clock=FixedClock(clock_instant))
    client = AbraxasClient(context=ctx)

    analyze = client.analyze(
        run_id=run_id,
        input_payload={"goal": alembic_task.get("goal"), "drill": True},
        alembic_task=alembic_task,
        enable_alembic=True,
        activation_lane="LOCAL_DEV",
    )
    receipt_rel = "out/production_convergence/recovery_drill/advisory_receipt.json"
    stamped = ctx.storage.write_artifact(
        receipt_rel,
        {
            "drill": "production_convergence_recovery",
            "recorded_at": ctx.clock.now_utc_iso(),
            "analyze": analyze,
            "alembic_task": alembic_task,
        },
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )

    # Replay prefers alembic.task on the analyze result when present.
    replay_source = analyze if isinstance(analyze.get("alembic"), dict) else stamped
    replay = client.replay(replay_source, run_id=f"{run_id}-replay")

    restamped = ctx.storage.write_artifact(
        receipt_rel,
        {
            "drill": "production_convergence_recovery",
            "recorded_at": ctx.clock.now_utc_iso(),
            "analyze": analyze,
            "alembic_task": alembic_task,
        },
        artifact_class=ArtifactClass.AUDIT_EVIDENCE,
    )

    on_disk = json.loads((work_dir / receipt_rel).read_text(encoding="utf-8"))
    return {
        "status": "OK"
        if analyze.get("status") == "OK" and replay.get("status") == "OK"
        else "DEGRADED",
        "analyze_status": analyze.get("status"),
        "replay_status": replay.get("status"),
        "receipt_path": receipt_rel,
        "receipt_hash": stamped["canonical_hash"],
        "receipt_hash_stable": stamped["canonical_hash"] == restamped["canonical_hash"],
        "on_disk_hash_matches": on_disk.get("canonical_hash") == stamped["canonical_hash"],
        "recorded_at": ctx.clock.now_utc_iso(),
        "candidate_status": "NOT_READY",
        "provider_id": ctx.provider.provider_id,
    }
