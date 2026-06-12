from __future__ import annotations

from afe.batch import build_hybrid_batch


def test_notion_payload_shape_is_local_only() -> None:
    packet = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=1,
        seed_start=42,
        environment_set=("baseline",),
        export_target="notion",
    )
    row = packet["notion_payload_rows"][0]

    assert row["Run Name"] == "AFE-BATCH-001 Run 001"
    assert row["Run ID"] == "AFE-BATCH-001-RUN-001"
    assert row["Status"] == "OK"
    assert row["Authority"] == "SHADOW_ONLY_TRACE"
    assert row["Live Writeback"] == "__NO__"
    assert packet["agent_trace_intake_export"]["writeback_performed"] is False
    assert packet["live_notion_writeback"] is False


def test_hybrid_non_limitation_locks() -> None:
    packet = build_hybrid_batch(
        batch_id="AFE-BATCH-001",
        runs=1,
        seed_start=42,
        environment_set=("baseline",),
        export_target="notion",
    )

    assert set(packet["non_limitation_locks"].values()) == {False}
