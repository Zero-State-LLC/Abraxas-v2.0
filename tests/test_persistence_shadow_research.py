"""Synthetic reference conformance, not deployed-system or scientific evidence."""

import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from core.canonical.json import canonical_hash
from core.evaluation.persistence_shadow import (
    contamination_at_k,
    current_evidence,
    paired_influence,
    policy_transaction,
    projection_errors,
    report_supported,
)

NOW = "2026-11-20T16:00:00Z"
AUTHORITY = {
    "advisory_only": True,
    "execution_authority": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "production_activation_allowed": False,
}
POLICY = {"fixture://operator": 0, "fixture://document": 1}
SCHEMA = json.loads(
    (
        Path(__file__).resolve().parents[1]
        / "contracts/evaluation/persisted_claim.v1.schema.json"
    ).read_text()
)


def claim(name="a", value="old", **changes):
    data = {
        "schema_version": "PersistedClaim.v1",
        "claim_id": "pc-" + name,
        "subject_id": "synthetic-agent",
        "predicate": "setting",
        "value_digest": canonical_hash(value),
        "valid_from": "2026-11-19T00:00:00Z",
        "valid_to": None,
        "recorded_at": "2026-11-19T00:00:00Z",
        "source_ref": "fixture://operator",
        "authority_tier": "PRIMARY",
        "supersedes_claim_id": None,
        "revoked_at": None,
        "revocation_ref": None,
        "content_classification": "INTERNAL",
        "retention_class": "STANDARD",
        "epistemic_status": "OBSERVED",
        "authority": deepcopy(AUTHORITY),
    }
    data.update(changes)
    Draft202012Validator(SCHEMA, format_checker=FormatChecker()).validate(data)
    return data


def resolve(claims, **kwargs):
    return current_evidence(claims, as_of=NOW, source_precedence=POLICY, **kwargs)


@pytest.mark.parametrize("seed", range(3))
def test_supersession_and_deletion_do_not_resurrect_old_memory(seed):
    old = claim()
    new = claim("b", "new", supersedes_claim_id="pc-a")
    history = [old, new] if seed % 2 == 0 else [new, old]
    before = deepcopy(history)
    assert resolve(history)["claim_ids"] == ["pc-b"]
    assert (
        resolve(history, deleted_ids=frozenset({"pc-b"}))["status"] == "NOT_COMPUTABLE"
    )
    new["revoked_at"], new["revocation_ref"] = NOW, "fixture://revocation"
    assert resolve(history)["claim_ids"] == []
    # The resolver does not mutate inputs; only the deliberate injection above did.
    assert old == before[history.index(old)]


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("valid_to", "2026-11-18T00:00:00Z", "INVALID_INTERVAL"),
        ("valid_from", "invalid", "INVALID_METADATA"),
        ("source_ref", "fixture://unknown", "UNKNOWN_SOURCE_AUTHORITY"),
        ("supersedes_claim_id", "pc-missing", "INVALID_LINEAGE"),
    ],
)
def test_invalid_metadata_fails_closed(field, value, reason):
    data = claim()
    data[field] = value
    assert resolve([data])["reason"] == reason


def test_equal_authority_conflict_is_not_last_writer_wins():
    a, b = claim(), claim("b", "new", recorded_at="2026-11-20T00:00:00Z")
    assert resolve([a, b])["reason"] == "AUTHORITY_CONFLICT"
    assert resolve([a, b]) == resolve([b, a])


def test_source_precedence_is_explicit_and_cannot_forge_supersession():
    a = claim()
    b = claim("b", "untrusted", source_ref="fixture://document")
    assert resolve([a, b])["claim_ids"] == ["pc-a"]
    b["supersedes_claim_id"] = "pc-a"
    assert resolve([a, b])["reason"] == "UNAUTHORIZED_SUPERSESSION"


@pytest.mark.parametrize("field", ["valid_from", "recorded_at"])
def test_future_information_cannot_hide_current_state(field):
    b = claim(
        "b", "future", supersedes_claim_id="pc-a", **{field: "2026-11-21T00:00:00Z"}
    )
    assert resolve([claim(), b])["claim_ids"] == ["pc-a"]


def test_half_open_validity_boundary():
    assert resolve([claim(valid_to=NOW)])["status"] == "NOT_COMPUTABLE"


def test_unknown_missing_cycle_and_duplicate_claims():
    assert resolve([])["status"] == "NOT_COMPUTABLE"
    assert resolve([claim(), claim()])["reason"] == "DUPLICATE_ID"
    assert (
        resolve(
            [claim(supersedes_claim_id="pc-b"), claim("b", supersedes_claim_id="pc-a")]
        )["reason"]
        == "INVALID_LINEAGE"
    )
    data = claim()
    del data["recorded_at"]
    assert resolve([data])["status"] == "NOT_COMPUTABLE"


def test_top_one_correct_does_not_mask_context_contamination():
    result = contamination_at_k(["current", "stale", "revoked"], {"current"}, 5)
    assert result["contaminated"] == 2
    assert result["denominator"] == 3
    assert result["rate"] == pytest.approx(2 / 3)
    assert contamination_at_k([], {"current"}, 5)["rate"] is None


@pytest.mark.parametrize("k", [0, -1, True, 1.5])
def test_invalid_k_rejected(k):
    with pytest.raises(ValueError):
        contamination_at_k([], set(), k)


def pair():
    original = {
        "pre_state_hash": canonical_hash("state"),
        "policy_hash": canonical_hash("policy"),
        "model_version": "synthetic-v1",
        "seed": 0,
        "task_hash": canonical_hash("task"),
        "action_hash": canonical_hash("bad"),
        "violation": True,
        "task_success": False,
        "memory_ids": ["harmful", "benign"],
        "neutralized_id": None,
    }
    alternative = {
        **original,
        "memory_ids": ["benign"],
        "neutralized_id": "harmful",
        "action_hash": canonical_hash("good"),
        "violation": False,
        "task_success": True,
    }
    return original, alternative


def test_paired_influence_records_difference_not_general_causal_claim():
    result = paired_influence(*pair())
    assert result["violation_removed"] and result["task_recovered"]
    assert result["causal_generalization"] == "NOT_COMPUTABLE"


@pytest.mark.parametrize(
    "key", ["pre_state_hash", "policy_hash", "model_version", "seed", "task_hash"]
)
def test_unmatched_counterfactual_pair_is_not_computable(key):
    a, b = pair()
    b[key] = "different"
    assert paired_influence(a, b)["status"] == "NOT_COMPUTABLE"


def test_missing_and_multiple_memory_interventions_rejected():
    a, b = pair()
    b["memory_ids"] = []
    assert paired_influence(a, b)["status"] == "NOT_COMPUTABLE"
    del b["action_hash"]
    assert paired_influence(a, b)["status"] == "NOT_COMPUTABLE"


@pytest.mark.parametrize("hops", [1, 3, 8])
def test_multihop_sensitive_egress_is_denied_atomically(hops):
    resources = {"secret": "SENSITIVE", "report": "PUBLIC"}
    actions = []
    source = "secret"
    for i in range(hops):
        actions.append({"op": "copy", "source": source, "target": f"tmp-{i}"})
        source = f"tmp-{i}"
    actions.append({"op": "egress", "source": source})
    assert policy_transaction(resources, actions) == {
        "status": "DENY",
        "resources": resources,
        "committed": False,
    }
    assert resources == {"secret": "SENSITIVE", "report": "PUBLIC"}


def test_clean_egress_allowed_and_labels_persist_across_transactions():
    resources = {"secret": "SENSITIVE", "report": "PUBLIC"}
    assert (
        policy_transaction(resources, [{"op": "egress", "source": "report"}])["status"]
        == "ALLOW"
    )
    copied = policy_transaction(
        resources, [{"op": "copy", "source": "secret", "target": "report"}]
    )
    assert copied["resources"]["report"] == "SENSITIVE"
    assert (
        policy_transaction(copied["resources"], [{"op": "egress", "source": "report"}])[
            "status"
        ]
        == "DENY"
    )


@pytest.mark.parametrize(
    "op", ["database", "background", "shared_memory", "shell", "semantic_edit"]
)
def test_unmodeled_channels_never_receive_safety_attestation(op):
    resources = {"report": "PUBLIC"}
    result = policy_transaction(
        resources,
        [
            {"op": "copy", "source": "report", "target": "staged"},
            {"op": op, "source": "staged"},
        ],
    )
    assert result == {
        "status": "NOT_COMPUTABLE",
        "resources": resources,
        "committed": False,
    }


def projection():
    return {
        "issue": {
            "state": "OPEN",
            "origin": "OBSERVED",
            "source_refs": ["fixture://event-1"],
        },
        "dream": {
            "state": "GENERATED",
            "origin": "GENERATED",
            "source_refs": ["fixture://cycle-1"],
        },
        "persona": {"version": "approved-v1", "source_refs": ["fixture://approval-1"]},
        "soul": {"version": "approved-v1", "source_refs": ["fixture://approval-2"]},
    }


@pytest.mark.parametrize(
    "key,field,value",
    [
        ("issue", "state", "RESOLVED"),
        ("dream", "origin", "OBSERVED"),
        ("dream", "state", "APPROVED"),
        ("persona", "version", "unapproved-v2"),
        ("soul", "version", "unapproved-v2"),
        ("issue", "source_refs", []),
    ],
)
def test_compaction_dream_persona_and_soul_distortion_rejected(key, field, value):
    source = projection()
    compacted = deepcopy(source)
    compacted[key][field] = value
    assert projection_errors(source, compacted) == [
        "STATE_OR_PROVENANCE_DISTORTION:" + key
    ]


def test_projection_preserves_exact_required_predicates_not_text_length():
    source = projection()
    assert projection_errors(source, deepcopy(source)) == []
    assert projection_errors(source, {}) == [
        "OMITTED_STATE:" + k for k in sorted(source)
    ]
    assert projection_errors({}, source) == [
        "UNSUPPORTED_CLAIM:" + k for k in sorted(source)
    ]


def report_pair():
    claim_data = {
        "verification_ref": "fixture://test-1",
        "artifact_hash": canonical_hash("artifact"),
        "scope": "unit",
    }
    receipt = {
        "result": "PASS",
        "artifact_hash": claim_data["artifact_hash"],
        "scope": "unit",
        "kind": "verification",
        "origin": "OBSERVED",
        "revoked": False,
    }
    return claim_data, {"fixture://test-1": receipt}


@pytest.mark.parametrize(
    "key,value",
    [
        ("result", "FAIL"),
        ("artifact_hash", "stale"),
        ("scope", "production"),
        ("kind", "self_report"),
        ("origin", "GENERATED"),
        ("revoked", True),
    ],
)
def test_unfaithful_report_cannot_bind_to_wrong_receipt(key, value):
    c, receipts = report_pair()
    assert report_supported(c, receipts)
    receipts["fixture://test-1"][key] = value
    assert not report_supported(c, receipts)


def test_absent_report_evidence_is_not_success():
    c, _ = report_pair()
    assert not report_supported(c, {})


def test_twelve_repeats_of_reference_output_are_identical():
    # Harness repeatability only, NOT the independent two-version promotion gate.
    hashes = [
        canonical_hash(
            resolve([claim(), claim("b", "new", supersedes_claim_id="pc-a")])
        )
        for _ in range(12)
    ]
    assert len(set(hashes)) == 1
