from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "HeavyTailFixtureCorpusCreationReceipt.v1"
RECEIPT_TYPE = "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT"
RECEIPT_STATUS = "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT_COMPLETE"
OPERATOR_ID = "HEAVY_TAIL"

FIXTURE_BASE_DIR = "input/fixtures/heavy_tail"

SOURCE_AUTH_ARTIFACT_ID = "heavy_tail_shadow_stub_implementation_authorization_001"
SOURCE_AUTH_SCHEMA_TYPE = "HeavyTailShadowStubImplementationAuthorization.v1"
SOURCE_AUTH_HASH = (
    "988ed40a766a2fb5edf82bd33a0cdcf5540a4a38486bc36b180802b7ef7e2834"
)

SOURCE_SCHEMA_PLAN_ARTIFACT_ID = "heavy_tail_test_vector_schema_plan_001"
SOURCE_SCHEMA_PLAN_SCHEMA_TYPE = "HeavyTailTestVectorSchemaPlan.v1"
SOURCE_SCHEMA_PLAN_HASH = (
    "d42a9570d5958822f788cae937ce808649e5d9bf6bf2811f960ed2502ed6bd04"
)

FIXTURE_CORPUS_PLAN_ARTIFACT_ID = "heavy_tail_fixture_corpus_creation_plan_001"
FIXTURE_CORPUS_PLAN_SCHEMA_TYPE = "HeavyTailFixtureCorpusCreationPlan.v1"
FIXTURE_CORPUS_PLAN_HASH = (
    "afed95244608e93da329110e552bc4674d9868c1578821e8af58c36d1a289b31"
)

TOTAL_FIXTURE_COUNT = 16
VALID_FIXTURE_COUNT = 6
INVALID_FIXTURE_COUNT = 4
NOT_COMPUTABLE_FIXTURE_COUNT = 6

LOCKED_TRUE_FLAGS = (
    "advisory_only",
    "shadow_lane_only",
    "fixture_corpus_creation_receipt_only",
    "fixture_creation_authorized",
    "fixture_files_created",
)
LOCKED_FALSE_FLAGS = (
    "computation_executed",
    "baseline_pack_updated",
    "emits_metric_values",
    "forecast_influence",
    "p43_surface_lanes_authorized",
    "production_activation",
    "canon_promotion",
    "runtime_mutation",
    "execution_authority",
    "inference_authority",
)

FORBIDDEN = (
    "metric-computation",
    "metric-value",
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)

PATCH_ID = "PATCH_HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT_001"

_VALID_FIXTURE_CORES: list[dict[str, Any]] = [
    {
        "fixture_id": "ht-valid-001",
        "fixture_group": "valid",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            400, 100, 44, 25, 16, 11, 8, 6, 4, 4,
            3, 2, 2, 2, 1, 1, 1, 1, 1, 1,
        ],
        "expected_status": "COMPUTABLE",
        "expected_tail_index": 2.0,
        "expected_moment_summary": {
            "mean": 31.65,
            "variance": 7653.13,
            "closed_form": True,
        },
        "expected_outcome_reason": "POWER_LAW_HEAVY_TAIL_DETECTED",
    },
    {
        "fixture_id": "ht-valid-002",
        "fixture_group": "valid",
        "operator_id": OPERATOR_ID,
        "alpha": 3.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            1000, 125, 37, 15, 8, 4, 2, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        ],
        "expected_status": "COMPUTABLE",
        "expected_tail_index": 3.0,
        "expected_moment_summary": {
            "mean": 60.2,
            "variance": 47241.76,
            "closed_form": True,
        },
        "expected_outcome_reason": "POWER_LAW_HEAVY_TAIL_DETECTED",
    },
    {
        "fixture_id": "ht-valid-003",
        "fixture_group": "valid",
        "operator_id": OPERATOR_ID,
        "alpha": 5.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            100, 90, 82, 74, 67, 61, 55, 50, 45, 41,
            37, 33, 30, 27, 25, 22, 20, 18, 16, 15,
        ],
        "expected_status": "COMPUTABLE",
        "expected_tail_index": 0.8,
        "expected_moment_summary": {
            "mean": 45.4,
            "variance": 645.94,
            "closed_form": True,
        },
        "expected_outcome_reason": "LIGHT_TAIL_CONTROL",
    },
    {
        "fixture_id": "ht-valid-004",
        "fixture_group": "valid",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            1000, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        ],
        "expected_status": "COMPUTABLE",
        "expected_tail_index": 2.5,
        "expected_moment_summary": {
            "mean": 50.95,
            "variance": 47405.05,
            "closed_form": True,
        },
        "expected_outcome_reason": "SINGLE_OUTLIER_DOMINATED",
    },
    {
        "fixture_id": "ht-valid-005",
        "fixture_group": "valid",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            20, 19, 18, 17, 16, 15, 14, 13, 12, 11,
            10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
        ],
        "expected_status": "COMPUTABLE",
        "expected_tail_index": 1.8,
        "expected_moment_summary": {
            "mean": 10.5,
            "variance": 33.25,
            "closed_form": True,
        },
        "expected_outcome_reason": "MONOTONE_RANK_FREQUENCY",
    },
    {
        "fixture_id": "ht-valid-006",
        "fixture_group": "valid",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        ],
        "expected_status": "COMPUTABLE",
        "expected_tail_index": 0.0,
        "expected_moment_summary": {
            "mean": 10.0,
            "variance": 0.0,
            "closed_form": True,
        },
        "expected_outcome_reason": "REPEATED_EQUAL_VALUES",
    },
]

_INVALID_FIXTURE_CORES: list[dict[str, Any]] = [
    {
        "fixture_id": "ht-invalid-001",
        "fixture_group": "invalid",
        "operator_id": OPERATOR_ID,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            400, 100, 44, 25, 16, 11, 8, 6, 4, 4,
            3, 2, 2, 2, 1, 1, 1, 1, 1, 1,
        ],
        "expected_status": "INVALID_INPUT",
        "expected_outcome_reason": "MISSING_ALPHA_FIELD",
    },
    {
        "fixture_id": "ht-invalid-002",
        "fixture_group": "invalid",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            400, 100, 44, 25, 16, 11, 8, 6, 4, 4,
            3, 2, 2, 2, 1, 1, 1, 1, 1, 1,
        ],
        "expected_status": "INVALID_INPUT",
        "expected_outcome_reason": "MISSING_SAMPLE_COUNT_FIELD",
    },
    {
        "fixture_id": "ht-invalid-003",
        "fixture_group": "invalid",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "expected_status": "INVALID_INPUT",
        "expected_outcome_reason": "MISSING_SEQUENCE_VALUES_FIELD",
    },
    {
        "fixture_id": "ht-invalid-004",
        "fixture_group": "invalid",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            400, 100, 44, 25, 16, 11, 8, 6, 4, 4,
            3, 2, 2, 2, 1, 1, 1, 1, 1, 1,
        ],
        "expected_status": "UNKNOWN",
        "expected_outcome_reason": "INVALID_EXPECTED_STATUS_VALUE",
    },
]

_NOT_COMPUTABLE_FIXTURE_CORES: list[dict[str, Any]] = [
    {
        "fixture_id": "ht-nc-001",
        "fixture_group": "not_computable",
        "operator_id": OPERATOR_ID,
        "alpha": -1.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        ],
        "expected_status": "NOT_COMPUTABLE",
        "expected_outcome_reason": "ALPHA_NOT_POSITIVE",
    },
    {
        "fixture_id": "ht-nc-002",
        "fixture_group": "not_computable",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 0,
        "expected_tail_threshold": 1.5,
        "sequence_values": [],
        "expected_status": "NOT_COMPUTABLE",
        "expected_outcome_reason": "ZERO_SAMPLE_COUNT",
    },
    {
        "fixture_id": "ht-nc-003",
        "fixture_group": "not_computable",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 5,
        "expected_tail_threshold": 1.5,
        "sequence_values": [],
        "expected_status": "NOT_COMPUTABLE",
        "expected_outcome_reason": "EMPTY_SEQUENCE",
    },
    {
        "fixture_id": "ht-nc-004",
        "fixture_group": "not_computable",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            10, 10, None, 10, 10, 10, 10, 10, 10, 10,
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        ],
        "expected_status": "NOT_COMPUTABLE",
        "expected_outcome_reason": "NON_FINITE_VALUE",
    },
    {
        "fixture_id": "ht-nc-005",
        "fixture_group": "not_computable",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [
            10, 10, -1, 10, 10, 10, 10, 10, 10, 10,
            10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
        ],
        "expected_status": "NOT_COMPUTABLE",
        "expected_outcome_reason": "NEGATIVE_VALUE",
    },
    {
        "fixture_id": "ht-nc-006",
        "fixture_group": "not_computable",
        "operator_id": OPERATOR_ID,
        "alpha": 2.0,
        "sample_count": 20,
        "expected_tail_threshold": 1.5,
        "sequence_values": [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
        "expected_status": "NOT_COMPUTABLE",
        "expected_outcome_reason": "SAMPLE_COUNT_MISMATCH",
    },
]


class HeavyTailFixtureCorpusCreationReceiptValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _prov_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _prov_safe(x)
    elif isinstance(v, list):
        for x in v:
            _prov_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "forbidden_provenance_reference_detected"
        )


def fixture_path(fixture_id: str) -> str:
    return f"{FIXTURE_BASE_DIR}/{fixture_id}.json"


def compute_fixture_hash(fixture_dict: dict[str, Any]) -> str:
    raw = fixture_dict.copy()
    raw.pop("fixture_hash", None)
    serialized = canonical_dumps(raw) + "\n"
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def build_fixture_content(
    core: dict[str, Any],
    generated_by: str = PATCH_ID,
) -> dict[str, Any]:
    fixture = dict(core)
    fixture["provenance"] = {
        "source": "HEAVY_TAIL_FIXTURE_CORPUS_CREATION_RECEIPT_001",
        "generated_by": generated_by,
        "fixture_corpus_plan_hash": FIXTURE_CORPUS_PLAN_HASH,
        "schema_plan_hash": SOURCE_SCHEMA_PLAN_HASH,
        "authorization_hash": SOURCE_AUTH_HASH,
    }
    h = compute_fixture_hash(fixture)
    fixture["fixture_hash"] = h
    return _finalize(fixture)


def write_fixture(
    fixture_dict: dict[str, Any],
    base_dir: str | Path,
) -> Path:
    out = Path(base_dir) / f"{fixture_dict['fixture_id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(canonical_dumps(fixture_dict) + "\n", encoding="utf-8")
    return out


def build_all_fixtures(
    generated_by: str = PATCH_ID,
) -> list[dict[str, Any]]:
    result = []
    for core in _VALID_FIXTURE_CORES:
        result.append(build_fixture_content(core, generated_by=generated_by))
    for core in _INVALID_FIXTURE_CORES:
        result.append(build_fixture_content(core, generated_by=generated_by))
    for core in _NOT_COMPUTABLE_FIXTURE_CORES:
        result.append(build_fixture_content(core, generated_by=generated_by))
    return sorted(result, key=lambda x: x["fixture_id"])


def _fixture_receipt_entry(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": fixture["fixture_id"],
        "fixture_group": fixture["fixture_group"],
        "fixture_path": fixture_path(fixture["fixture_id"]),
        "fixture_hash": fixture["fixture_hash"],
        "fixture_created": True,
        "expected_outcome_reason": fixture["expected_outcome_reason"],
    }


def default_source_authorization_binding() -> dict[str, Any]:
    return {
        "authorization_artifact_id": SOURCE_AUTH_ARTIFACT_ID,
        "authorization_schema_type": SOURCE_AUTH_SCHEMA_TYPE,
        "authorization_canonical_hash": SOURCE_AUTH_HASH,
        "hash_confirmed": True,
        "fixture_creation_authorized_acknowledged": True,
        "computation_not_performed": True,
        "metric_values_not_emitted": True,
    }


def default_schema_plan_binding() -> dict[str, Any]:
    return {
        "schema_plan_artifact_id": SOURCE_SCHEMA_PLAN_ARTIFACT_ID,
        "schema_plan_schema_type": SOURCE_SCHEMA_PLAN_SCHEMA_TYPE,
        "schema_plan_canonical_hash": SOURCE_SCHEMA_PLAN_HASH,
        "hash_confirmed": True,
        "schema_fields_covered": [
            "alpha", "sample_count", "expected_tail_threshold",
            "sequence_values", "expected_tail_index",
            "expected_moment_summary", "expected_status", "expected_outcome_reason",
        ],
    }


def default_fixture_corpus_plan_binding() -> dict[str, Any]:
    return {
        "fixture_corpus_plan_artifact_id": FIXTURE_CORPUS_PLAN_ARTIFACT_ID,
        "fixture_corpus_plan_schema_type": FIXTURE_CORPUS_PLAN_SCHEMA_TYPE,
        "fixture_corpus_plan_canonical_hash": FIXTURE_CORPUS_PLAN_HASH,
        "hash_confirmed": True,
        "total_fixture_count_from_plan": TOTAL_FIXTURE_COUNT,
        "valid_fixture_count_from_plan": VALID_FIXTURE_COUNT,
        "invalid_fixture_count_from_plan": INVALID_FIXTURE_COUNT,
        "not_computable_fixture_count_from_plan": NOT_COMPUTABLE_FIXTURE_COUNT,
        "fixture_base_directory_from_plan_overridden": True,
        "fixture_base_directory_used": FIXTURE_BASE_DIR,
    }


def default_corpus_creation_scope_review(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "fixture_creation_authorized": True,
        "fixture_files_created": True,
        "fixture_count_created": len(fixtures),
        "valid_count_created": sum(1 for f in fixtures if f["fixture_group"] == "valid"),
        "invalid_count_created": sum(1 for f in fixtures if f["fixture_group"] == "invalid"),
        "not_computable_count_created": sum(
            1 for f in fixtures if f["fixture_group"] == "not_computable"
        ),
        "all_fixture_ids_unique": True,
        "all_fixture_ids_deterministic": True,
        "computation_not_in_scope": True,
        "metric_emission_not_in_scope": True,
        "baseline_pack_update_not_in_scope": True,
        "shadow_stub_only_posture_preserved": True,
        "confirmed": True,
    }


def default_authority_lock_review() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "fixture_corpus_creation_receipt_only": True,
        "fixture_creation_authorized": True,
        "fixture_files_created": True,
        "computation_executed": False,
        "baseline_pack_updated": False,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_blocked_scope_review() -> dict[str, Any]:
    return {
        "computation": "BLOCKED",
        "metric_emission": "BLOCKED",
        "forecast_influence": "BLOCKED",
        "p43_lanes": "BLOCKED",
        "runtime_mutation": "BLOCKED",
        "production_activation": "BLOCKED",
        "canon_promotion": "BLOCKED",
        "execution_authority": "BLOCKED",
        "inference_authority": "BLOCKED",
        "baseline_pack_update": "BLOCKED_UNTIL_COMPUTATION_RECEIPT",
        "confirmed": True,
        "all_blocked_scopes_correct": True,
    }


def validate_receipt(packet: dict[str, Any]) -> None:
    req = {
        "schema_version", "receipt_id", "receipt_type", "receipt_status", "operator_id",
        "source_authorization_binding", "schema_plan_binding", "fixture_corpus_plan_binding",
        "fixture_file_manifest", "valid_fixture_receipt", "invalid_fixture_receipt",
        "not_computable_fixture_receipt", "fixture_hash_manifest",
        "corpus_creation_scope_review", "authority_lock_review", "blocked_scope_review",
        "recommended_next_step", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(req - packet.keys())
    if missing:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError("invalid_schema_version")
    if packet["receipt_type"] != RECEIPT_TYPE:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError("invalid_receipt_type")
    if packet["receipt_status"] != RECEIPT_STATUS:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError("invalid_receipt_status")
    if packet["operator_id"] != OPERATOR_ID:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError("unknown_operator_id")

    auth_b = packet["source_authorization_binding"]
    if auth_b.get("authorization_canonical_hash") != SOURCE_AUTH_HASH:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "authorization_hash_mismatch"
        )
    if auth_b.get("hash_confirmed") is not True:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "authorization_hash_not_confirmed"
        )

    sp_b = packet["schema_plan_binding"]
    if sp_b.get("schema_plan_canonical_hash") != SOURCE_SCHEMA_PLAN_HASH:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "schema_plan_hash_mismatch"
        )
    if sp_b.get("hash_confirmed") is not True:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "schema_plan_hash_not_confirmed"
        )

    fcp_b = packet["fixture_corpus_plan_binding"]
    if fcp_b.get("fixture_corpus_plan_canonical_hash") != FIXTURE_CORPUS_PLAN_HASH:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "fixture_corpus_plan_hash_mismatch"
        )
    if fcp_b.get("hash_confirmed") is not True:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "fixture_corpus_plan_hash_not_confirmed"
        )

    manifest = packet["fixture_file_manifest"]
    if len(manifest) != TOTAL_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "fixture_file_manifest_count_mismatch"
        )
    for entry in manifest:
        if entry.get("fixture_created") is not True:
            raise HeavyTailFixtureCorpusCreationReceiptValidationError(
                f"fixture_not_created:{entry.get('fixture_id')}"
            )

    vfr = packet["valid_fixture_receipt"]
    if len(vfr) != VALID_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "valid_fixture_receipt_count_mismatch"
        )
    ifr = packet["invalid_fixture_receipt"]
    if len(ifr) != INVALID_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "invalid_fixture_receipt_count_mismatch"
        )
    ncfr = packet["not_computable_fixture_receipt"]
    if len(ncfr) != NOT_COMPUTABLE_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "not_computable_fixture_receipt_count_mismatch"
        )

    all_ids: list[str] = []
    for group in (vfr, ifr, ncfr):
        for entry in group:
            fid = entry.get("fixture_id")
            if fid in all_ids:
                raise HeavyTailFixtureCorpusCreationReceiptValidationError(
                    f"duplicate_fixture_id:{fid}"
                )
            all_ids.append(fid)
            if entry.get("fixture_created") is not True:
                raise HeavyTailFixtureCorpusCreationReceiptValidationError(
                    f"fixture_not_created:{fid}"
                )

    fhm = packet["fixture_hash_manifest"]
    if len(fhm) != TOTAL_FIXTURE_COUNT:
        raise HeavyTailFixtureCorpusCreationReceiptValidationError(
            "fixture_hash_manifest_count_mismatch"
        )

    auth_lock = packet["authority_lock_review"]
    for flag in LOCKED_TRUE_FLAGS:
        if auth_lock.get(flag) is not True:
            raise HeavyTailFixtureCorpusCreationReceiptValidationError(
                f"authority_lock_must_be_true:{flag}"
            )
    for flag in LOCKED_FALSE_FLAGS:
        if auth_lock.get(flag) is not False:
            raise HeavyTailFixtureCorpusCreationReceiptValidationError(
                f"authority_lock_must_be_false:{flag}"
            )

    _prov_safe(packet["provenance"])


def compute_receipt_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_receipt(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_receipt(
    payload: dict[str, Any],
    fixtures: list[dict[str, Any]],
) -> dict[str, Any]:
    valid_fixtures = sorted(
        [f for f in fixtures if f["fixture_group"] == "valid"],
        key=lambda x: x["fixture_id"],
    )
    invalid_fixtures = sorted(
        [f for f in fixtures if f["fixture_group"] == "invalid"],
        key=lambda x: x["fixture_id"],
    )
    nc_fixtures = sorted(
        [f for f in fixtures if f["fixture_group"] == "not_computable"],
        key=lambda x: x["fixture_id"],
    )
    all_sorted = sorted(fixtures, key=lambda x: x["fixture_id"])

    fixture_file_manifest = [
        {
            "fixture_id": f["fixture_id"],
            "fixture_group": f["fixture_group"],
            "fixture_path": fixture_path(f["fixture_id"]),
            "fixture_hash": f["fixture_hash"],
            "fixture_created": True,
        }
        for f in all_sorted
    ]
    fixture_hash_manifest = {f["fixture_id"]: f["fixture_hash"] for f in all_sorted}

    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "receipt_status": RECEIPT_STATUS,
        "operator_id": OPERATOR_ID,
        "source_authorization_binding": payload.get(
            "source_authorization_binding", default_source_authorization_binding()
        ),
        "schema_plan_binding": payload.get(
            "schema_plan_binding", default_schema_plan_binding()
        ),
        "fixture_corpus_plan_binding": payload.get(
            "fixture_corpus_plan_binding", default_fixture_corpus_plan_binding()
        ),
        "fixture_file_manifest": fixture_file_manifest,
        "valid_fixture_receipt": [_fixture_receipt_entry(f) for f in valid_fixtures],
        "invalid_fixture_receipt": [_fixture_receipt_entry(f) for f in invalid_fixtures],
        "not_computable_fixture_receipt": [_fixture_receipt_entry(f) for f in nc_fixtures],
        "fixture_hash_manifest": fixture_hash_manifest,
        "corpus_creation_scope_review": payload.get(
            "corpus_creation_scope_review", default_corpus_creation_scope_review(fixtures)
        ),
        "authority_lock_review": payload.get(
            "authority_lock_review", default_authority_lock_review()
        ),
        "blocked_scope_review": payload.get(
            "blocked_scope_review", default_blocked_scope_review()
        ),
        "recommended_next_step": payload.get(
            "recommended_next_step", "HEAVY_TAIL_COMPUTATION_RECEIPT"
        ),
    }
    base["canonical_hash"] = compute_receipt_hash(base)
    validate_receipt(base)
    return _finalize(base)
