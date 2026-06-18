from __future__ import annotations

from typing import Any

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene.contracts.v2_hygiene_rune_base import V2HygieneRune
from abraxas.v2.hygiene.loop_dynamics import LoopDynamics
from abraxas.v2.hygiene.registers import V2Output


class LoopAwarenessRune(V2HygieneRune):
    rune_id = "RUNE.LOOP_AWARENESS"

    def apply(self, content: V2Output, context: dict[str, Any], mode: HygieneMode) -> V2Output:
        if mode == HygieneMode.OFF:
            return content
        dynamics = content.loop_dynamics or LoopDynamics(
            retrocausal_risk=float(context.get("retrocausal_risk", 0.0)),
            hyperstitional_charge=float(context.get("hyperstitional_charge", 0.0)),
            mitigation=str(context.get("mitigation", "advisory_loop_tag")),
        )
        provenance = dict(content.provenance)
        provenance["loop_awareness"] = {"mode": mode.value, "rune_id": self.rune_id}
        return content.model_copy(update={"loop_dynamics": dynamics, "provenance": provenance})
