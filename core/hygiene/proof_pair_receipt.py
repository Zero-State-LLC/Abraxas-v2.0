"""ProofPairReceipt.v1 — advisory Soft Facade for POSITIVE_PROOF / NEGATIVE_PROOF.

Does not replace the individual proof runes. Completely optional.
execution_authority is hard-coded False. net_catalog_delta = 0.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional
import hashlib
import json

POLARITIES = ("POSITIVE_PROOF", "NEGATIVE_PROOF")
PolaritySummary = Literal["POSITIVE", "NEGATIVE", "BOTH", "NEITHER"]


@dataclass
class ProofPairReceipt:
    """Advisory composite. Does not replace individual proof runes."""

    receipt_type: str = "ProofPairReceipt.v1"
    schema_version: str = "ProofPairReceipt.v1"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    producer_system: str = "GROK"
    execution_authority: bool = False
    net_catalog_delta: int = 0
    applied_polarities: Dict[str, bool] = field(default_factory=dict)
    polarity_summary: PolaritySummary = "NEITHER"
    source_receipts: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    provenance_hash: str = ""
    recommended_next: str = "OPERATOR_REVIEW"
    provenance: Dict = field(default_factory=dict)

    def finalize(self) -> "ProofPairReceipt":
        pos = self.applied_polarities.get("POSITIVE_PROOF", False)
        neg = self.applied_polarities.get("NEGATIVE_PROOF", False)
        if pos and neg:
            self.polarity_summary = "BOTH"
        elif pos:
            self.polarity_summary = "POSITIVE"
        elif neg:
            self.polarity_summary = "NEGATIVE"
        else:
            self.polarity_summary = "NEITHER"

        payload = {
            "receipt_type": self.receipt_type,
            "schema_version": self.schema_version,
            "producer_system": self.producer_system,
            "execution_authority": self.execution_authority,
            "net_catalog_delta": self.net_catalog_delta,
            "applied_polarities": self.applied_polarities,
            "polarity_summary": self.polarity_summary,
            "source_receipts": sorted(self.source_receipts),
            "notes": self.notes,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.provenance_hash = hashlib.sha256(raw).hexdigest()
        self.provenance = {
            "generator": "ProofPairReceipt.v1-advisory-0.1",
            "producer_system": self.producer_system,
            "registers": {"classification": "OBSERVED"},
            "loop_dynamics": {
                "assessment_complete": True,
                "retrocausal_risk": "NONE",
            },
            "hash": self.provenance_hash,
        }
        return self

    def to_dict(self) -> dict:
        return asdict(self)


def emit_proof_pair_receipt(
    applied: List[str],
    source_receipts: Optional[List[str]] = None,
    notes: Optional[str] = None,
    producer_system: str = "GROK",
) -> ProofPairReceipt:
    """Thin advisory helper. Individual POSITIVE_PROOF / NEGATIVE_PROOF remain authoritative."""
    applied_set = {p.upper() for p in applied}
    applied_map = {p: (p in applied_set) for p in POLARITIES}
    receipt = ProofPairReceipt(
        producer_system=producer_system,
        applied_polarities=applied_map,
        source_receipts=source_receipts or [],
        notes=notes,
    )
    return receipt.finalize()
