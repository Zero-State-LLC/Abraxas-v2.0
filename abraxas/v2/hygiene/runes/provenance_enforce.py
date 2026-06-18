from __future__ import annotations

from typing import Any

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene.contracts.v2_hygiene_rune_base import V2HygieneRune
from abraxas.v2.hygiene.registers import V2Output


class ProvenanceEnforceRune(V2HygieneRune):
    rune_id = "RUNE.PROVENANCE_ENFORCE"

    def apply(self, content: V2Output, context: dict[str, Any], mode: HygieneMode) -> V2Output:
        if mode == HygieneMode.OFF:
            return content
        provenance = dict(content.provenance)
        provenance.setdefault("source", context.get("source", "unknown"))
        provenance["provenance_enforced"] = mode.value
        return content.model_copy(update={"provenance": provenance})
