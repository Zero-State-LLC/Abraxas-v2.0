"""v2 hygiene runes."""

from abraxas.v2.hygiene.runes.adversarial_audit import AdversarialAuditRune
from abraxas.v2.hygiene.runes.hyperstition_tag import HyperstitionTagRune
from abraxas.v2.hygiene.runes.loop_awareness import LoopAwarenessRune
from abraxas.v2.hygiene.runes.output_register_enforce import OutputRegisterEnforceRune
from abraxas.v2.hygiene.runes.provenance_enforce import ProvenanceEnforceRune

DEFAULT_RUNES = (
    LoopAwarenessRune(),
    ProvenanceEnforceRune(),
    HyperstitionTagRune(),
    AdversarialAuditRune(),
    OutputRegisterEnforceRune(),
)

__all__ = [
    "AdversarialAuditRune",
    "DEFAULT_RUNES",
    "HyperstitionTagRune",
    "LoopAwarenessRune",
    "OutputRegisterEnforceRune",
    "ProvenanceEnforceRune",
]
