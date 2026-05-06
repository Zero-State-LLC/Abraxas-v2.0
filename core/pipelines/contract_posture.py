from __future__ import annotations

from enum import Enum


class ContractPosture(str, Enum):
    current = "current"
    legacy_accepted = "legacy_accepted"
    legacy_needs_upgrade = "legacy_needs_upgrade"
    invalid = "invalid"
    not_computable = "not_computable"
