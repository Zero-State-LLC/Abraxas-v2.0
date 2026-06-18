from __future__ import annotations

import os
from typing import Any, Iterable

from abraxas.v2.governance.mode import HygieneMode, resolve_hygiene_mode
from abraxas.v2.hygiene.contracts.v2_hygiene_rune_base import V2HygieneRune
from abraxas.v2.hygiene.registers import V2Output
from abraxas.v2.hygiene.runes import DEFAULT_RUNES


class HygienePipeline:
    def __init__(
        self,
        runes: Iterable[V2HygieneRune] | None = None,
        mode: HygieneMode | None = None,
    ) -> None:
        self.runes = tuple(runes or DEFAULT_RUNES)
        self.mode = mode or resolve_hygiene_mode()

    @classmethod
    def from_env(cls, env: os._Environ[str] | None = None) -> "HygienePipeline":
        return cls(mode=resolve_hygiene_mode(env))

    def enabled(self) -> bool:
        return self.mode != HygieneMode.OFF

    def process(self, content: V2Output, context: dict[str, Any] | None = None) -> V2Output:
        if not self.enabled():
            return content
        ctx = context or {}
        result = content
        for rune in self.runes:
            if rune.supports_mode(self.mode):
                result = rune.apply(result, ctx, self.mode)
        return result
