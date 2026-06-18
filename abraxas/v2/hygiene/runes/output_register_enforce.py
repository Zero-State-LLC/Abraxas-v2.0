from __future__ import annotations

from typing import Any

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene.contracts.v2_hygiene_rune_base import V2HygieneRune
from abraxas.v2.hygiene.registers import RegisterTier, V2Output


class OutputRegisterEnforceRune(V2HygieneRune):
    rune_id = "RUNE.OUTPUT_REGISTER_ENFORCE"

    def apply(self, content: V2Output, context: dict[str, Any], mode: HygieneMode) -> V2Output:
        if mode == HygieneMode.OFF:
            return content
        required_tier = context.get("required_tier", RegisterTier.OBSERVED.value)
        if mode == HygieneMode.STRICT and not content.tier(RegisterTier(required_tier)):
            raise ValueError(f"required tier missing: {required_tier}")
        provenance = dict(content.provenance)
        provenance["output_register_enforced"] = required_tier
        return content.model_copy(update={"provenance": provenance})
