from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.generated_artifact_registry import build_generated_artifact_registry
from core.ingest.runtime_handoff_executor import (
    AUTHORITY,
    SOURCE_PATCH_ID,
    TARGET_PATCH_ID,
    build_oracle_intake_queue,
    build_runtime_handoff_receipt_set,
    build_sample_manifest_and_config,
    build_source_pull_receipt_set,
    write_runtime_handoff_outputs,
)


def test_runtime_handoff_is_stable_and_non_authoritative() -> None:
    manifest, config = build_sample_manifest_and_config()
    pull_a = build_source_pull_receipt_set(manifest, config)
    handoff_a = build_runtime_handoff_receipt_set(manifest, config, source_pull_receipt_set=pull_a)
    queue_a = build_oracle_intake_queue(manifest, config, runtime_handoff_receipt_set=handoff_a)

    pull_b = build_source_pull_receipt_set(manifest, config)
    handoff_b = build_runtime_handoff_receipt_set(manifest, config, source_pull_receipt_set=pull_b)
    queue_b = build_oracle_intake_queue(manifest, config, runtime_handoff_receipt_set=handoff_b)

    assert pull_a == pull_b
    assert handoff_a == handoff_b
    assert queue_a == queue_b
    assert handoff_a["authority"] == AUTHORITY
    assert handoff_a["source_manifest_patch_id"] == SOURCE_PATCH_ID
    assert handoff_a["patch_id"] == TARGET_PATCH_ID
    assert [row["adapter_id"] for row in handoff_a["receipts"]] == ["abx_market_feed_v1"]
    assert handoff_a["receipts"][0]["handoff_status"] == "QUEUE_READY_ADVISORY_ONLY"
    assert queue_a["queue_entries"][0]["queue_status"] == "READY_FOR_ORACLE_INTAKE"


def test_runtime_handoff_fails_closed_for_missing_eligible_adapter() -> None:
    manifest, config = build_sample_manifest_and_config()
    config["adapters"] = [row for row in config["adapters"] if row["adapter_id"] != "abx_market_feed_v1"]
    with pytest.raises(ValueError, match="missing adapter config"):
        build_source_pull_receipt_set(manifest, config)


def test_runtime_handoff_contracts_and_registry() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    manifest, config = build_sample_manifest_and_config()
    pull = build_source_pull_receipt_set(manifest, config)
    handoff = build_runtime_handoff_receipt_set(manifest, config, source_pull_receipt_set=pull)
    queue = build_oracle_intake_queue(manifest, config, runtime_handoff_receipt_set=handoff)

    contract_dir = Path("contracts/ingest")
    jsonschema.validate(config, json.loads((contract_dir / "source_adapter_config_set.v1.schema.json").read_text(encoding="utf-8")))
    jsonschema.validate(pull, json.loads((contract_dir / "source_pull_receipt_set.v1.schema.json").read_text(encoding="utf-8")))
    jsonschema.validate(handoff, json.loads((contract_dir / "runtime_handoff_receipt_set.v1.schema.json").read_text(encoding="utf-8")))
    jsonschema.validate(queue, json.loads((contract_dir / "oracle_intake_queue.v1.schema.json").read_text(encoding="utf-8")))

    out = Path("out/ingest/_tmp_runtime_handoff_receipt_set.latest.json")
    write_runtime_handoff_outputs(
        out.parent,
        runtime_handoff_receipt_set=handoff,
        source_pull_receipt_set=pull,
        oracle_intake_queue=queue,
    )
    assert (out.parent / "runtime_handoff_receipt_set_001.latest.md").read_text(encoding="utf-8").endswith("\n")

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {entry.artifact_path: entry for entry in registry.entries}
    assert emap["out/ingest/runtime_handoff_receipt_set_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/ingest/source_pull_receipt_set_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/ingest/oracle_intake_queue_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"

    for path in (
        out.parent / "runtime_handoff_receipt_set_001.latest.json",
        out.parent / "runtime_handoff_receipt_set_001.latest.md",
        out.parent / "source_pull_receipt_set_001.latest.json",
        out.parent / "source_pull_receipt_set_001.latest.md",
        out.parent / "oracle_intake_queue_001.latest.json",
        out.parent / "oracle_intake_queue_001.latest.md",
    ):
        path.unlink(missing_ok=True)
