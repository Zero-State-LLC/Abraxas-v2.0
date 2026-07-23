from core.oracle.compositional_memory_adapter import adapt_oracle_evidence_to_compositional_memory


def test_adapter_emits_deterministic_advisory_memory_packet() -> None:
    items = [
        {
            "signal_id": "visual-1",
            "source": "fixture-image",
            "timestamp": "2026-07-23T00:00:00Z",
            "evidence_type": "image",
            "content_hash": "sha256:shared",
            "modality": "visual",
            "lane": "OBSERVED",
            "provenance": {"source": "fixture", "lineage": "artifact-1"},
            "semantic_tags": ["camera", "signal"],
        },
        {
            "signal_id": "text-1",
            "source": "fixture-text",
            "timestamp": "2026-07-23T00:00:01Z",
            "evidence_type": "text",
            "content_hash": "sha256:shared",
            "modality": "textual",
            "lane": "INFERRED",
            "provenance": {"source": "fixture", "lineage": "artifact-1"},
            "semantic_tags": ["camera"],
        },
    ]

    first = adapt_oracle_evidence_to_compositional_memory(items)
    second = adapt_oracle_evidence_to_compositional_memory(list(reversed(items)))

    assert first == second
    assert first["status"] == "ORACLE_COMPOSITIONAL_MEMORY_ADAPTED_ADVISORY_ONLY"
    assert first["input_count"] == 2
    assert first["lanes"] == ["INFERRED", "OBSERVED"]
    assert first["memory_packet"]["connector_count"] == 1
    assert first["memory_packet"]["entry_count"] == 2
    assert first["model_inference"] is False
    assert first["embedding_search"] is False
    assert first["forecast_routing"] is False
    assert first["execution_authority"] is False
    assert first["advisory_only"] is True


def test_adapter_preserves_oracle_lane_and_lineage_in_provenance() -> None:
    receipt = adapt_oracle_evidence_to_compositional_memory(
        [
            {
                "signal_id": "signal-1",
                "source": "fixture",
                "timestamp": "2026-07-23T00:00:00Z",
                "evidence_type": "observation",
                "content_hash": "sha256:signal-1",
                "modality": "textual",
                "lane": "SPECULATIVE",
                "provenance": {"lineage": "source-1"},
                "semantic_tags": ["alpha", "alpha"],
            }
        ]
    )

    entry = receipt["memory_packet"]["textual_memory"][0]
    assert entry["memory_id"] == "oracle:signal-1"
    assert entry["semantic_tags"] == ["alpha"]
    assert entry["provenance"]["lineage"] == "source-1"
    assert entry["provenance"]["oracle_lane"] == "SPECULATIVE"
    assert entry["provenance"]["oracle_signal_id"] == "signal-1"


def test_adapter_empty_input_fails_closed_as_not_computable() -> None:
    receipt = adapt_oracle_evidence_to_compositional_memory([])

    assert receipt["status"] == "NOT_COMPUTABLE"
    assert receipt["reason"] == "NO_NORMALIZED_ORACLE_EVIDENCE"
    assert receipt["memory_packet"] is None
    assert receipt["truth_assignment"] is False
    assert receipt["forecast_routing"] is False
    assert receipt["runtime_mutation"] is False
    assert receipt["execution_authority"] is False
