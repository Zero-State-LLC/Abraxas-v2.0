"""Synthetic omission tests. No live concurrency or model efficacy attestation."""

from copy import deepcopy

import pytest

from core.evaluation.persistence_shadow import (
    compaction_admission,
    evidence_completeness,
    recall_boundary,
    resolve_entity,
)


def packet(revision="r1"):
    return [
        {"source_ref": "source:a", "revision": revision, "role": role}
        for role in ("claim", "enrichment", "materialized_source")
    ]


ROLES = {"claim", "enrichment", "materialized_source"}


@pytest.mark.parametrize("pause_after", [0, 1, 2, 3])
def test_update_at_each_read_boundary_requires_retry(pause_after):
    # Deterministic schedule, not probabilistic thread timing: begin at epoch 2,
    # read prefix, publish r2 at epoch 4, then read suffix and end epoch.
    records = packet()[:pause_after] + packet("r2")[pause_after:]
    assert recall_boundary(2, 4, "CLEAN", {"source:a": "r1"}, records, ROLES) == "RETRY"
    assert (
        recall_boundary(4, 4, "CLEAN", {"source:a": "r2"}, packet("r2"), ROLES)
        == "READY"
    )


def test_mixed_revisions_cannot_hide_behind_equal_epochs():
    records = packet()
    records[-1]["revision"] = "r2"
    assert (
        recall_boundary(2, 2, "CLEAN", {"source:a": "r1"}, records, ROLES)
        == "NOT_COMPUTABLE"
    )


@pytest.mark.parametrize("index", [0, 1, 2])
def test_missing_role_and_duplicate_do_not_make_complete_packet(index):
    records = packet()
    records.pop(index)
    records.append(deepcopy(records[0]))
    assert (
        recall_boundary(2, 2, "CLEAN", {"source:a": "r1"}, records, ROLES)
        == "NOT_COMPUTABLE"
    )


def test_dirty_failure_stays_closed_until_explicit_recovery():
    assert (
        recall_boundary(2, 2, "DIRTY", {"source:a": "r1"}, packet(), ROLES) == "RETRY"
    )
    assert (
        recall_boundary(3, 3, "CLEAN", {"source:a": "r1"}, packet(), ROLES) == "RETRY"
    )
    assert (
        recall_boundary(4, 4, "CLEAN", {"source:a": "r2"}, packet("r2"), ROLES)
        == "READY"
    )


@pytest.mark.parametrize("epoch", [-1, True, 2.0])
def test_invalid_epoch_is_not_a_snapshot(epoch):
    assert (
        recall_boundary(epoch, epoch, "CLEAN", {"source:a": "r1"}, packet(), ROLES)
        == "NOT_COMPUTABLE"
    )


def test_each_source_requires_every_declared_role():
    assert (
        recall_boundary(
            2, 2, "CLEAN", {"source:a": "r1", "source:b": "r7"}, packet(), ROLES
        )
        == "NOT_COMPUTABLE"
    )
    records = packet() + [
        dict(r, source_ref="source:b", revision="r7") for r in packet()
    ]
    assert (
        recall_boundary(
            2, 2, "CLEAN", {"source:a": "r1", "source:b": "r7"}, records, ROLES
        )
        == "READY"
    )


@pytest.mark.parametrize("mutation", ["missing", "unknown_source", "unknown_role"])
def test_unbound_read_record_is_not_complete(mutation):
    records = packet()
    if mutation == "missing":
        del records[0]["revision"]
    elif mutation == "unknown_source":
        records[0]["source_ref"] = "source:unknown"
    else:
        records[0]["role"] = "unknown"
    assert (
        recall_boundary(2, 2, "CLEAN", {"source:a": "r1"}, records, ROLES)
        == "NOT_COMPUTABLE"
    )


@pytest.mark.parametrize("name", ["Alex", " ALEX "])
def test_namesakes_abstain_until_identified(name):
    entities = {"person:a": ["Alex"], "person:b": ["Alex", "A. B."]}
    before = deepcopy(entities)
    assert resolve_entity(entities, name=name)["status"] == "NOT_COMPUTABLE"
    assert (
        resolve_entity(entities, name=name, subject_id="person:b")["subject_id"]
        == "person:b"
    )
    assert entities == before


@pytest.mark.parametrize("identity", ["person:unknown", "person:excluded"])
def test_unknown_or_excluded_id_cannot_fall_back_to_namesake(identity):
    assert (
        resolve_entity({"person:a": ["Alex"]}, name="Alex", subject_id=identity)[
            "subject_id"
        ]
        is None
    )


def test_unique_alias_is_not_entity_merge_authority():
    entities = {"person:a": ["Alex"], "person:b": ["Alexander"]}
    assert resolve_entity(entities, name="Alexa")["status"] == "NOT_COMPUTABLE"
    assert (
        resolve_entity(entities, name="Alexander", subject_id="person:a")["status"]
        == "NOT_COMPUTABLE"
    )
    assert resolve_entity(entities, name="Alex")["subject_id"] == "person:a"
    assert resolve_entity(entities, name="")["status"] == "NOT_COMPUTABLE"


GOLD = [
    ("source:a", "r1", 0, 10),
    ("source:b", "r1", 20, 30),
    ("source:c", "r2", 5, 15),
]


def score(spans, cost=30, budget=30):
    return evidence_completeness(GOLD, spans, token_cost=cost, token_budget=budget)


def test_complete_support_is_not_top_one_relevance():
    assert score(GOLD[:1])["covered"] == 1
    assert score(GOLD[:1])["complete"] is False
    assert score(GOLD)["complete"] is True
    assert score(GOLD, cost=31)["complete"] is False


def test_fragments_union_without_duplicate_credit_or_revision_leakage():
    fragments = [("source:a", "r1", 0, 5), ("source:a", "r1", 4, 10)] + GOLD[1:]
    assert score(fragments + fragments)["covered"] == 3
    fragments[1] = ("source:a", "r2", 4, 10)
    assert score(fragments)["covered"] == 2
    fragments[1] = ("source:a", "r1", 6, 10)
    assert score(fragments)["covered"] == 2


@pytest.mark.parametrize("cost,budget", [(-1, 30), (True, 30), (1, 0), (1, 2.5)])
def test_invalid_token_accounting_is_unknown(cost, budget):
    assert score(GOLD, cost, budget)["status"] == "NOT_COMPUTABLE"


def test_empty_gold_is_unknown_and_empty_retrieval_is_incomplete():
    assert (
        evidence_completeness([], [], token_cost=0, token_budget=30)["complete"] is None
    )
    assert score([])["complete"] is False
    assert score([("source:a", "r1", 10, 0)])["status"] == "NOT_COMPUTABLE"


def state(version=1):
    return {
        "decision": {"version": version, "source_refs": [f"source:r{version}"]},
        "dream": {"origin": "GENERATED", "approved": False},
    }


def admit(frozen, current, projection, **changes):
    args = {
        "frozen_epoch": 2,
        "current_epoch": 2,
        "frozen_policy": "p1",
        "current_policy": "p1",
    }
    args.update(changes)
    return compaction_admission(frozen, current, projection, **args)


def test_three_compaction_cycles_preserve_required_state():
    # Identity projection is a positive control, not an LLM summarizer.
    for cycle in range(3):
        frozen = state(cycle + 1)
        assert (
            admit(
                frozen,
                deepcopy(frozen),
                deepcopy(frozen),
                frozen_epoch=2 * cycle,
                current_epoch=2 * cycle,
            )
            == "READY"
        )


@pytest.mark.parametrize(
    "change", ["correction", "deletion", "policy", "epoch", "dream"]
)
def test_background_summary_cannot_commit_stale_state(change):
    frozen, current, projection = state(), state(), state()
    kwargs = {}
    if change == "correction":
        current = state(2)
    elif change == "deletion":
        del current["decision"]
    elif change == "policy":
        kwargs["current_policy"] = "p2"
    elif change == "epoch":
        kwargs["current_epoch"] = 4
    else:
        projection["dream"]["origin"] = "OBSERVED"
    assert admit(frozen, current, projection, **kwargs) != "READY"
    assert frozen == state()


@pytest.mark.parametrize(
    "field,value",
    [("current_epoch", True), ("current_epoch", 3), ("current_policy", "")],
)
def test_unbound_compaction_is_not_admitted(field, value):
    assert admit(state(), state(), state(), **{field: value}) == "NOT_COMPUTABLE"


def maintenance_trace(*, internal_repair, external_repair):
    """Declared toy dynamics, not an empirical biological or agent model."""
    health = 2
    trajectory = []
    for _ in range(3):
        health = max(0, health - 1)
        if internal_repair or external_repair:
            health += 1
        trajectory.append(health)
    return trajectory


def test_ordinary_continuity_cannot_identify_self_maintenance():
    internal = maintenance_trace(internal_repair=True, external_repair=False)
    external = maintenance_trace(internal_repair=False, external_repair=True)
    assert internal == external
    # Declared matched intervention removes external repair only.
    withdrawn = maintenance_trace(internal_repair=False, external_repair=False)
    assert internal != withdrawn
    # Separating these two stipulated models does not establish causal closure.
