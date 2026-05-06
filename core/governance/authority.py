"""Governance authority model for ABRAXAS v2.0.

All authority flags default to False.  Any True flag is a doctrine violation.
"""

from __future__ import annotations

from pydantic import BaseModel, model_validator


class Authority(BaseModel):
    """Explicit authority boundary model.

    Every flag defaults to False.  The system fails closed: any True flag
    triggers an authority violation detected by assert_locked().
    """

    promotion_allowed: bool = False
    forecast_weight_allowed: bool = False
    runtime_mutation_allowed: bool = False
    baseline_mutation_allowed: bool = False
    canon_mutation_allowed: bool = False
    aal_viz_inference_authority: bool = False

    model_config = {"frozen": True}

    def forbidden_true_flags(self) -> list[str]:
        """Return names of all flags that are set to True."""
        return [field for field, val in self.model_dump().items() if val is True]

    def assert_locked(self) -> None:
        """Raise ValueError if any authority flag is True."""
        bad = self.forbidden_true_flags()
        if bad:
            raise ValueError(f"Authority violation – flags set True: {bad}")

    @model_validator(mode="after")
    def _all_must_be_false(self) -> "Authority":
        self.assert_locked()
        return self


def locked_authority() -> dict[str, bool]:
    """Return a dict representing a fully-locked (all-false) authority."""
    return Authority().model_dump()
