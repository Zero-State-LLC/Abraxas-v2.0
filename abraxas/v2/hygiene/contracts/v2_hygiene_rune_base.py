from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from abraxas.v2.governance.mode import HygieneMode
from abraxas.v2.hygiene.registers import V2Output


class V2HygieneRune(ABC):
    rune_id: str
    version: str = "1.0.0"
    owner_module: str = "abraxas.v2.hygiene"

    @abstractmethod
    def apply(self, content: V2Output, context: dict[str, Any], mode: HygieneMode) -> V2Output:
        """Apply hygiene transformation; ADVISORY must not mutate primary register content."""

    def supports_mode(self, mode: HygieneMode) -> bool:
        return mode in {HygieneMode.ADVISORY, HygieneMode.STRICT}
