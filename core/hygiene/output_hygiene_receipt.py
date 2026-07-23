"""OutputHygieneReceipt.v1 — advisory Soft Facade for Output Enforcer runes.

Does not replace individual enforcer runes. Completely optional.
execution_authority is hard-coded False. net_catalog_delta = 0.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
import hashlib
import json

ENFORCERS = (
    "PROVENANCE_ENFORCE",
    "OUTPUT_REGISTER_ENFORCE",
    "LOOP_AWARENESS",
    "HYPERSTITION_TAG",
    "ADVERSARIAL_AUDIT",
)


@dataclass
class OutputHygieneReceipt:
    """Advisory composite. Does not replace individual enforcer runes."""

    receipt_type: str = "OutputHygieneReceipt.v1"
    schema_version: str = "OutputHygieneReceipt.v1"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    producer_system: str = "GROK"
    execution_authority: bool = False
    net_catalog_delta: int = 0
    applied_enforcers: Dict[str, bool] = field(default_factory=dict)
    register_summary: Dict[str, List[str]] = field(
        default_factory=lambda: {"OBSERVED": [], "INFERRED": [], "SPECULATIVE": []}
    )
    source_receipts: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    provenance_hash: str = ""
    recommended_next: str = "OPERATOR_REVIEW"
    provenance: Dict = field(default_factory=dict)

    def finalize(self) -> "OutputHygieneReceipt":
        payload = {
            "receipt_type": self.receipt_type,
            "schema_version": self.schema_version,
            "producer_system": self.producer_system,
            "execution_authority": self.execution_authority,
            "net_catalog_delta": self.net_catalog_delta,
            "applied_enforcers": self.applied_enforcers,
            "register_summary": self.register_summary,
            "source_receipts": sorted(self.source_receipts),
            "notes": self.notes,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        self.provenance_hash = hashlib.sha256(raw).hexdigest()
        self.provenance = {
            "generator": "OutputHygieneReceipt.v1-hygiene-0.2",
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


def emit_output_hygiene_receipt(
    applied: List[str],
    source_receipts: Optional[List[str]] = None,
    register_summary: Optional[Dict[str, List[str]]] = None,
    notes: Optional[str] = None,
    producer_system: str = "GROK",
) -> OutputHygieneReceipt:
    """Thin advisory helper. Individual enforcer runes remain authoritative."""
    applied_set = {e.upper() for e in applied}
    applied_map = {e: (e in applied_set) for e in ENFORCERS}
    receipt = OutputHygieneReceipt(
        producer_system=producer_system,
        applied_enforcers=applied_map,
        register_summary=register_summary
        or {"OBSERVED": [], "INFERRED": [], "SPECULATIVE": []},
        source_receipts=source_receipts or [],
        notes=notes,
    )
    return receipt.finalize()
