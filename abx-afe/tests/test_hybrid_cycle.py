from __future__ import annotations

from afe.batch import build_hybrid_batch


def test_hybrid_batch_identity_is_deterministic() -> None:
    first = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=10,
        seed_start=42,
        environment_set=("baseline", "scarcity", "high-noise"),
        export_target="notion",
    )
    second = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=10,
        seed_start=42,
        environment_set=("baseline", "scarcity", "high-noise"),
        export_target="notion",
    )

    assert first == second
    assert first["status"] == "OK"
    assert first["authority"] == "SHADOW_ONLY_TRACE"
    assert len(first["runs"]) == 10
    assert len(first["notion_payload_rows"]) == 10


def test_hybrid_batch_metric_bounds() -> None:
    packet = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=5,
        seed_start=42,
        environment_set=("baseline", "scarcity"),
        export_target="notion",
    )

    for row in packet["notion_payload_rows"]:
        for key in ("ACS", "MDI", "SES", "SLI", "ECI"):
            assert 0.0 <= row[key] <= 1.0


def test_hybrid_batch_not_computable_behavior() -> None:
    packet = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=0,
        seed_start=42,
        environment_set=("baseline",),
        export_target="notion",
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["not_computable_reasons"] == ["RUN_COUNT_MUST_BE_POSITIVE"]
    assert packet["live_notion_writeback"] is False
