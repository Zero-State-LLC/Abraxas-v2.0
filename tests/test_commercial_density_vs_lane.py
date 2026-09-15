"""Patch C: density gate is not a lane lock."""

from pathlib import Path


def test_contract_doc_exists():
    root = Path(__file__).resolve().parents[1]
    path = root / "docs/contracts/COMMERCIAL_DENSITY_VS_LANE.md"
    text = path.read_text(encoding="utf-8")
    assert "density gate" in text.lower()
    assert "lane lock" in text.lower()


def test_receipt_schema_describes_density_not_lane():
    root = Path(__file__).resolve().parents[1]
    schema = (root / "contracts/ingest/familiar_ingestion_receipt.v0.schema.json").read_text(
        encoding="utf-8"
    )
    assert "Not a SHADOW lane lock" in schema
    assert "commercial_claims_blocked" in schema
