from core.oracle.evidence import SourceEvidencePacket


def test_evidence_hash_deterministic() -> None:
    assert SourceEvidencePacket.compute_hash("h", ["a"], "structural") == SourceEvidencePacket.compute_hash("h", ["a"], "structural")
