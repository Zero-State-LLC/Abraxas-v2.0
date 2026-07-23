# core/temporal_formula_export_helper_stub.py
# Advisory export helper: TemporalFormula + regime sequence → offline-friendly artifact
# Produces a receipt + a simple textual representation suitable for human review
# or future offline Spot/HOA translation. No external tool is invoked.
# No execution authority.

from __future__ import annotations
from typing import Any, Dict, List, Mapping, Sequence
from datetime import datetime, timezone
import json

class TemporalFormulaExportHelper:
    """Advisory stub that exports a TemporalFormula + regime sequence
    into a structured offline artifact. Does not call any external checker.
    """

    VERSION = "0.1-advisory-stub"

    def __init__(self):
        self.execution_authority = False

    def export(
        self,
        formula: Mapping[str, Any],
        regime_sequence: Sequence[str],
        formula_id: str = "formula-001",
    ) -> Dict[str, Any]:
        """Create an offline export receipt + human-readable summary."""

        # Very simple LTL-like string rendering for human review only
        rendered = self._render_formula(formula)

        receipt = {
            "artifact_type": "TemporalFormulaExportReceipt.v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SHADOW_EXPORTED",
            "execution_authority": False,
            "formula_id": formula_id,
            "formula": dict(formula),
            "regime_sequence": list(regime_sequence),
            "rendered_ltl_style": rendered,
            "notes": [
                "This artifact is for offline human review or future sandboxed translation only.",
                "No external model checker is invoked by this helper.",
                "Import of any external verification result must remain receipt-only.",
            ],
            "provenance": f"{self.VERSION} | temporal_formula_export_helper_stub",
            "recommended_next": "OPERATOR_REVIEW_OR_OFFLINE_TOOL_USE",
        }
        return receipt

    def _render_formula(self, node: Mapping[str, Any]) -> str:
        """Conservative string rendering of the structured formula."""
        op = node.get("operator")
        operands = node.get("operands", [])

        if op == "ATOMIC":
            if operands and "atomic" in operands[0]:
                return str(operands[0]["atomic"])
            return "?"

        if op == "ALWAYS":
            return f"G({self._render_formula(operands[0])})" if operands else "G(?)"

        if op == "EVENTUALLY":
            return f"F({self._render_formula(operands[0])})" if operands else "F(?)"

        if op == "NEXT":
            return f"X({self._render_formula(operands[0])})" if operands else "X(?)"

        if op == "NOT":
            return f"!({self._render_formula(operands[0])})" if operands else "!(?)"

        if op == "AND":
            parts = [self._render_formula(o) for o in operands]
            return "(" + " & ".join(parts) + ")"

        if op == "OR":
            parts = [self._render_formula(o) for o in operands]
            return "(" + " | ".join(parts) + ")"

        if op == "UNTIL":
            if len(operands) >= 2:
                return f"({self._render_formula(operands[0])} U {self._render_formula(operands[1])})"
            return "(? U ?)"

        return "?"


# Dry-run example
if __name__ == "__main__":
    helper = TemporalFormulaExportHelper()
    formula = {
        "schema_version": "TemporalFormula.v1",
        "operator": "ALWAYS",
        "operands": [{"atomic": "STABLE"}],
    }
    receipt = helper.export(formula, ["STABLE", "STABLE", "TRANSITIONING"])
    print(json.dumps(receipt, indent=2))
