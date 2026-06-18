from __future__ import annotations

from typing import Any

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene.contracts.v2_hygiene_rune_base import V2HygieneRune
from abraxas.v2.hygiene.registers import V2Output


class HyperstitionTagRune(V2HygieneRune):
    rune_id = "RUNE.HYPERSTITION_TAG"

    def apply(self, content: V2Output, context: dict[str, Any], mode: HygieneMode) -> V2Output:
        if mode == HygieneMode.OFF:
            return content
        provenance = dict(content.provenance)
        tag = str(context.get("hyperstition_tag", "UNTAGGED"))
        provenance["hyperstition_tag"] = tag
        if mode == HygieneMode.STRICT and tag == "UNTAGGED":
            raise ValueError("hyperstition tag required in STRICT mode")
        return content.model_copy(update={"provenance": provenance})
