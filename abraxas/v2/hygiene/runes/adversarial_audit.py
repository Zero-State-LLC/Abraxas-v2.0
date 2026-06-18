from __future__ import annotations

from typing import Any

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene.contracts.v2_hygiene_rune_base import V2HygieneRune
from abraxas.v2.hygiene.registers import V2Output


class AdversarialAuditRune(V2HygieneRune):
    rune_id = "RUNE.ADVERSARIAL_AUDIT"

    def apply(self, content: V2Output, context: dict[str, Any], mode: HygieneMode) -> V2Output:
        if mode == HygieneMode.OFF:
            return content
        provenance = dict(content.provenance)
        findings = list(context.get("adversarial_findings", []))
        provenance["adversarial_audit"] = {"findings": findings, "mode": mode.value}
        if mode == HygieneMode.STRICT and findings:
            raise ValueError("adversarial findings block STRICT promotion")
        return content.model_copy(update={"provenance": provenance})
