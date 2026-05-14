from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.canonical.json import canonical_dumps
from core.human_decision_continuity.chains import HumanDecisionChainPacket


def _chain_kwargs(
    *,
    chain_id: str = "hdc-1",
    root_decision_hash: str = "decision-root-1",
    continuity_chain_count: int = 1,
) -> dict[str, object]:
    return {
        "chain_id": chain_id,
        "root_decision_hash": root_decision_hash,
        "continuity_chain_count": continuity_chain_count,
        "deterministic_chain_hash": HumanDecisionChainPacket.compute_hash(
            root_decision_hash, continuity_chain_count
        ),
        "status": "passed",
    }


def test_continuity_chain_hash_is_deterministic() -> None:
    payload = _chain_kwargs()
    packet_a = HumanDecisionChainPacket(**payload)
    packet_b = HumanDecisionChainPacket(**payload)
    assert packet_a.deterministic_chain_hash == packet_b.deterministic_chain_hash
    assert packet_a.deterministic_chain_hash == HumanDecisionChainPacket.compute_hash(
        "decision-root-1", 1
    )


def test_chain_identity_and_canonical_payload_are_stable() -> None:
    payload = _chain_kwargs()
    packet_a = HumanDecisionChainPacket(**payload)
    packet_b = HumanDecisionChainPacket(**payload)
    assert packet_a.chain_id == packet_b.chain_id == "hdc-1"
    assert canonical_dumps(packet_a.model_dump()) == canonical_dumps(packet_b.model_dump())


def test_broken_continuity_is_detected() -> None:
    payload = _chain_kwargs()
    payload["deterministic_chain_hash"] = "tampered"
    with pytest.raises(ValidationError, match="chain hash"):
        HumanDecisionChainPacket(**payload)


def test_missing_predecessor_state_is_explicitly_rejected() -> None:
    payload = _chain_kwargs()
    del payload["root_decision_hash"]
    with pytest.raises(ValidationError):
        HumanDecisionChainPacket(**payload)


def test_duplicate_chain_node_is_blocked_by_nonadvancing_count() -> None:
    with pytest.raises(ValidationError, match="continuity chain must advance"):
        HumanDecisionChainPacket(**_chain_kwargs(continuity_chain_count=0))


def test_no_silent_continuity_fabrication_under_authority_violation() -> None:
    payload = _chain_kwargs()
    payload["authority"] = {"promotion_allowed": True}
    with pytest.raises(ValidationError, match="Authority violation"):
        HumanDecisionChainPacket(**payload)
