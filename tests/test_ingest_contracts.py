from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.ingest import DEFAULT_INGEST_REGISTRY


def test_ingest_adapter_schema_validates_registry_descriptors() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/ingest/ingest_adapter.v1.schema.json").read_text(encoding="utf-8")
    )

    for descriptor in DEFAULT_INGEST_REGISTRY.list_descriptors():
        jsonschema.validate(descriptor.model_dump(mode="json"), schema)


def test_ingest_packet_schema_validates_json_adapter_packet(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/ingest/ingest_packet.v1.schema.json").read_text(encoding="utf-8")
    )
    source = tmp_path / "payload.json"
    source.write_text(
        json.dumps({"statement": "Observed structured payload.", "status": "OBSERVED"}),
        encoding="utf-8",
    )

    packet = DEFAULT_INGEST_REGISTRY.ingest(tmp_path, source)
    jsonschema.validate(packet.model_dump(mode="json"), schema)


def test_source_record_schema_validates_filesystem_source(tmp_path: Path) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/ingest/source_record.v1.schema.json").read_text(encoding="utf-8")
    )
    source = tmp_path / "notes.txt"
    source.write_text("observed text", encoding="utf-8")

    packet = DEFAULT_INGEST_REGISTRY.ingest(tmp_path, source)
    jsonschema.validate(packet.source_record.model_dump(mode="json"), schema)
