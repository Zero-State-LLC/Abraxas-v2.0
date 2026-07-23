# core/temporal_formula_checker_stub.py
# Advisory Temporal Formula Checker (restricted LTL-style)
# Evaluates structured TemporalFormula.v1 against a sequence of regime statuses.
# Shadow / projection only. No execution authority.

from __future__ import annotations
from typing import Any, Dict, List, Mapping, Sequence
from datetime import datetime, timezone
import json

class TemporalFormulaChecker:
    """Advisory stub for evaluating restricted temporal formulas.
    Accepts only the structured TemporalFormula.v1 schema.
    Returns a receipt; never mutates state or issues commands.
    """

    VERSION = "0.1-advisory-stub"

    def __init__(self):
        self.execution_authority = False

    def evaluate(
        self,
        formula: Mapping[str, Any],
        regime_sequence: Sequence[str],
    ) -> Dict[str, Any]:
        """Evaluate a TemporalFormula against a linear sequence of temporal_status values.
        regime_sequence items must be one of: STABLE, TRANSITIONING, UNSTABLE, NOT_COMPUTABLE.
        """
        receipt = {
            "artifact_type": "TemporalFormulaEvaluationReceipt.v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "SHADOW_EVALUATED",
            "execution_authority": False,
            "formula": dict(formula),
            "regime_sequence": list(regime_sequence),
            "result": "NOT_COMPUTABLE",
            "provenance": f"{self.VERSION} | temporal_formula_checker_stub",
            "recommended_next": "OPERATOR_REVIEW",
        }

        try:
            result = self._eval(formula, list(regime_sequence))
            receipt["result"] = result
            receipt["status"] = "SHADOW_EVALUATED_SUCCESS"
        except Exception as e:
            receipt["error"] = str(e)
            receipt["status"] = "SHADOW_EVALUATION_FAILED"

        return receipt

    def _eval(self, node: Mapping[str, Any], seq: List[str]) -> str:
        op = node.get("operator")
        operands = node.get("operands", [])

        if op == "ATOMIC":
            if not operands or "atomic" not in operands[0]:
                return "NOT_COMPUTABLE"
            target = operands[0]["atomic"]
            # True if the entire observed sequence matches the atomic proposition
            return "TRUE" if all(s == target for s in seq) else "FALSE"

        if op == "ALWAYS":  # □
            if not operands:
                return "NOT_COMPUTABLE"
            sub = self._eval(operands[0], seq)
            return "TRUE" if sub == "TRUE" else "FALSE"

        if op == "EVENTUALLY":  # ◇
            if not operands:
                return "NOT_COMPUTABLE"
            # Simplified: true if the sub-formula holds on any suffix
            for i in range(len(seq)):
                if self._eval(operands[0], seq[i:]) == "TRUE":
                    return "TRUE"
            return "FALSE"

        if op == "NEXT":  # ○
            if not operands or len(seq) < 2:
                return "NOT_COMPUTABLE"
            return self._eval(operands[0], seq[1:])

        if op == "AND":
            results = [self._eval(o, seq) for o in operands]
            if any(r == "NOT_COMPUTABLE" for r in results):
                return "NOT_COMPUTABLE"
            return "TRUE" if all(r == "TRUE" for r in results) else "FALSE"

        if op == "OR":
            results = [self._eval(o, seq) for o in operands]
            if any(r == "TRUE" for r in results):
                return "TRUE"
            if all(r == "FALSE" for r in results):
                return "FALSE"
            return "NOT_COMPUTABLE"

        if op == "NOT":
            if not operands:
                return "NOT_COMPUTABLE"
            sub = self._eval(operands[0], seq)
            if sub == "TRUE":
                return "FALSE"
            if sub == "FALSE":
                return "TRUE"
            return "NOT_COMPUTABLE"

        if op == "UNTIL":
            # Simplified linear until
            if len(operands) < 2:
                return "NOT_COMPUTABLE"
            # Very conservative implementation for advisory use
            return "NOT_COMPUTABLE"

        return "NOT_COMPUTABLE"


# Dry-run example
if __name__ == "__main__":
    checker = TemporalFormulaChecker()

    # Example: ALWAYS STABLE
    formula = {
        "schema_version": "TemporalFormula.v1",
        "operator": "ALWAYS",
        "operands": [{"atomic": "STABLE"}],
    }

    receipt = checker.evaluate(formula, ["STABLE", "STABLE", "STABLE"])
    print(json.dumps(receipt, indent=2))

    receipt2 = checker.evaluate(formula, ["STABLE", "TRANSITIONING", "STABLE"])
    print("\nSecond evaluation:")
    print(json.dumps(receipt2, indent=2))
