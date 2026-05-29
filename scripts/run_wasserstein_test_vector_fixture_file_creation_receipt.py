"""Script: emit WassersteinTestVectorFixtureFileCreationReceipt.v1 artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.canonical.json import canonical_dumps, canonical_hash
from core.config import RuntimePaths
from core.diagnostics import get_structured_logger, log_event, stable_correlation_id

PATCH_ID = (
    "PATCH_P52_WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_RECEIPT_001"
)
SCHEMA_VERSION = "WassersteinTestVectorFixtureFileCreationReceipt.v1"
RECEIPT_ID = "wasserstein_test_vector_fixture_file_creation_receipt_001"
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)
FIXTURE_ROOT = Path("input/fixtures/wasserstein")

_PATHS = RuntimePaths.from_env()
OUT_PATH = _PATHS.wasserstein_test_vector_fixture_file_creation_receipt_latest

EXPECTED_VALID_IDS = [
    "valid-001", "valid-002", "valid-003", "valid-004", "valid-005",
]
EXPECTED_INVALID_IDS = [
    "invalid-001", "invalid-002", "invalid-003", "invalid-004", "invalid-005",
]
EXPECTED_NC_IDS = ["nc-001", "nc-002", "nc-003", "nc-004"]


def _scan_group(directory: Path) -> list[dict]:
    entries = []
    for p in sorted(directory.glob("*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        entries.append({
            "fixture_id": doc["fixture_id"],
            "fixture_type": doc["fixture_type"],
            "fixture_group": doc["fixture_group"],
            "target_path": str(p),
            "fixture_creation_authorized": doc["fixture_creation_authorized"],
            "metric_value_emitted": doc["metric_value_emitted"],
            "expected_wasserstein_distance_included": (
                doc["expected_wasserstein_distance_included"]
            ),
            "source_gate_hash_verified": doc["source_gate_hash"] == SOURCE_GATE_HASH,
        })
    return entries


def main() -> int:
    logger = get_structured_logger(__name__)
    correlation_id = stable_correlation_id(
        "wasserstein_test_vector_fixture_file_creation_receipt",
        artifact_path=OUT_PATH,
        context={"patch_id": PATCH_ID},
    )
    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_file_creation_receipt_started",
        artifact_path=OUT_PATH.as_posix(),
        correlation_id=correlation_id,
    )

    valid_entries = _scan_group(FIXTURE_ROOT / "valid")
    invalid_entries = _scan_group(FIXTURE_ROOT / "invalid")
    nc_entries = _scan_group(FIXTURE_ROOT / "not_computable")

    total = len(valid_entries) + len(invalid_entries) + len(nc_entries)
    if total != 14:
        raise RuntimeError(f"fixture_count_mismatch: expected 14, found {total}")

    all_gate_hashes_verified = all(
        e["source_gate_hash_verified"]
        for e in valid_entries + invalid_entries + nc_entries
    )
    if not all_gate_hashes_verified:
        raise RuntimeError("source_gate_hash_verification_failed")

    packet: dict = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "source_gate_hash": SOURCE_GATE_HASH,
        "intended_lane": "SHADOW",
        "receipt_status": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE"
        ),
        "fixture_files_created": True,
        "fixture_file_creation_authorized": True,
        "fixture_count_created": total,
        "valid_count_created": len(valid_entries),
        "invalid_count_created": len(invalid_entries),
        "not_computable_count_created": len(nc_entries),
        "batch_count_created": 3,
        "created_fixture_manifest": {
            "valid": valid_entries,
            "invalid": invalid_entries,
            "not_computable": nc_entries,
        },
        "authority_locks": {
            "fixture_files_created": True,
            "fixture_file_creation_authorized": True,
            "wasserstein_computation_authorized": False,
            "emits_metric_values": False,
            "expected_wasserstein_distances_added": False,
            "forecast_influence": False,
            "p43_surface_lanes_authorized": False,
            "production_activation": False,
            "canon_promotion": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "inference_authority": False,
        },
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_COMPLETE_REVIEW"
        ),
        "provenance": {
            "source": "P52_WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_RECEIPT",
            "evidence_refs": [
                "WassersteinTestVectorFixtureCreationActualPRGate.v1:"
                "wasserstein_test_vector_fixture_creation_actual_pr_gate_001",
            ],
            "generated_by": PATCH_ID,
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_file_creation_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }

    packet["canonical_hash"] = canonical_hash(
        {k: v for k, v in packet.items() if k != "canonical_hash"}
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(canonical_dumps(packet) + "\n", encoding="utf-8")

    log_event(
        logger,
        "INFO",
        "wasserstein_test_vector_fixture_file_creation_receipt_completed",
        artifact_path=OUT_PATH.as_posix(),
        canonical_hash=packet["canonical_hash"],
        fixture_count_created=total,
        correlation_id=correlation_id,
    )
    print(f"receipt_id={packet['receipt_id']}")
    print(f"receipt_status={packet['receipt_status']}")
    print(f"fixture_files_created={packet['fixture_files_created']}")
    print(f"fixture_count_created={packet['fixture_count_created']}")
    print(f"valid_count_created={packet['valid_count_created']}")
    print(f"invalid_count_created={packet['invalid_count_created']}")
    print(f"not_computable_count_created={packet['not_computable_count_created']}")
    print(f"source_gate_hash={packet['source_gate_hash']}")
    print(f"canonical_hash={packet['canonical_hash']}")
    print(f"wrote={OUT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
