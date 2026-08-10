"""Shared contract-validation report shape for canonical contract layers.

Convergence layer: ``core/settlement/``, ``core/replay_execution/``, and
``core/replay_ledger/`` previously each defined an identical
``*ValidationFinding`` / ``*ValidationReport`` pair plus duplicated canonical
JSON + SHA-256 receipt helpers. This module is the single shape and the single
receipt-hash construction; the per-layer names remain as aliases.

Receipt hashes are byte-identical to the pre-convergence implementations:
the payload is ``{"status": ..., "findings": [...], <subject_key>: <id>}``
serialized with the canonical JSON algorithm (sorted keys, minimal separators,
unicode preserved). Payloads contain no floats, so canonical float
normalization is a no-op here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from core.canonical.json import canonical_hash


@dataclass(frozen=True)
class ContractValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ContractValidationReport:
    status: str
    findings: tuple[ContractValidationFinding, ...]
    receipt_hash: str


def build_validation_report(
    status: str,
    findings: list[ContractValidationFinding] | tuple[ContractValidationFinding, ...],
    *,
    subject_key: str,
    subject_id: str,
) -> ContractValidationReport:
    """Assemble a report with the canonical receipt hash.

    *subject_key* preserves each layer's historical receipt payload key
    (``settlement_id``, ``replay_id``, ``ledger_id``, ``diff_id``) so existing
    receipt hashes remain stable.
    """
    receipt_hash = canonical_hash(
        {"status": status, "findings": [asdict(f) for f in findings], subject_key: subject_id}
    )
    return ContractValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)
