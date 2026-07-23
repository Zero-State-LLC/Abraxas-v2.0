import json
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path("contracts/engineering/agent_artifact_metadata.v1.schema.json")


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_accepts_mixed_peer_artifact() -> None:
    payload = {
        "schema_version": "AgentArtifactMetadata.v1",
        "artifact_id": "oracle-memory-adapter-001",
        "producer_system": "MIXED",
        "producer_version": None,
        "implementation_surface": "core/oracle/compositional_memory_adapter.py",
        "contract_version": "NormalizedOracleEvidence.v1",
        "depends_on": ["CompositionalMemoryPacket.v1"],
        "supersedes": [],
        "tests": ["tests/test_oracle_compositional_memory_adapter.py"],
        "evidence": ["PR #987"],
        "branch": "codex/oracle-compositional-memory-adapter",
        "pull_request": 987,
        "merge_sha": None,
        "status": "IMPLEMENTED_IN_BRANCH",
        "authority": {
            "producer_identity_grants_authority": False,
            "auto_supersession": False,
            "auto_canon_promotion": False,
            "auto_merge": False,
            "operator_review_on_conflict": True,
        },
    }

    Draft202012Validator(_schema()).validate(payload)


def test_schema_rejects_producer_authority_escalation() -> None:
    payload = {
        "schema_version": "AgentArtifactMetadata.v1",
        "artifact_id": "invalid-authority",
        "producer_system": "GROK",
        "implementation_surface": "core/example.py",
        "contract_version": "Example.v1",
        "depends_on": [],
        "supersedes": [],
        "tests": [],
        "evidence": [],
        "status": "PROPOSED",
        "authority": {
            "producer_identity_grants_authority": True,
            "auto_supersession": False,
            "auto_canon_promotion": False,
            "auto_merge": False,
            "operator_review_on_conflict": True,
        },
    }

    errors = list(Draft202012Validator(_schema()).iter_errors(payload))
    assert errors
