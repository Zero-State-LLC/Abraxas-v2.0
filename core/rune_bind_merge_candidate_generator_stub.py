# core/rune_bind_merge_candidate_generator_stub.py
# Advisory candidate generator for Bind/Merge First doctrine.
# Produces ranked merge/bind proposals only. Never applies merges.
# No execution authority. Expansion remains operator-gated.

from __future__ import annotations
from typing import Any, Dict, List, Mapping, Optional, Sequence
from datetime import datetime, timezone
import json

class RuneBindMergeCandidateGenerator:
    """Advisory stub that proposes bind/merge candidates.
    Does not mutate the catalog or binding matrix.
    """

    VERSION = "0.1-advisory-stub"

    def __init__(self):
        self.execution_authority = False

    def propose_candidates(
        self,
        runes: Sequence[Mapping[str, Any]],
        similarity_threshold: float = 0.75,
    ) -> Dict[str, Any]:
        """Generate ranked merge/bind candidates from a list of rune records.

        Each rune is expected to have at least:
          - id (str)
          - purpose (str) or description (str)
          - authority_locks (dict, optional)
        """
        candidates: List[Dict[str, Any]] = []

        # Naive pairwise similarity on purpose/description tokens
        for i, a in enumerate(runes):
            for b in runes[i + 1 :]:
                score = self._similarity(a, b)
                if score >= similarity_threshold:
                    lock_ok = self._locks_compatible(a, b)
                    survivor, loser = self._choose_survivor(a, b)
                    candidates.append({
                        "survivors": [survivor],
                        "merged_away": [loser],
                        "similarity_score": score,
                        "authority_locks_compatible": lock_ok,
                        "net_catalog_delta": -1,
                        "quality_rationale": (
                            f"High semantic overlap ({score:.2f}). "
                            f"Proposed survivor: {survivor}."
                        ),
                        "expansion_performed": False,
                    })

        # Rank by similarity descending
        candidates.sort(key=lambda c: c["similarity_score"], reverse=True)

        receipt = {
            "artifact_type": "RuneBindMergeReceipt.v1",
            "schema_version": "RuneBindMergeReceipt.v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "CANDIDATE_PROPOSAL",
            "survivors": [],
            "merged_away": [],
            "net_catalog_delta": 0,
            "quality_rationale": "Candidate generation only; no merges applied.",
            "authority_locks_preserved": True,
            "expansion_performed": False,
            "execution_authority": False,
            "operator_seal": None,
            "provenance": f"{self.VERSION} | rune_bind_merge_candidate_generator_stub",
            "recommended_next": "OPERATOR_REVIEW_OF_CANDIDATES",
            "candidates": candidates,
            "candidate_count": len(candidates),
        }
        return receipt

    def _similarity(self, a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
        text_a = (a.get("purpose") or a.get("description") or "").lower()
        text_b = (b.get("purpose") or b.get("description") or "").lower()
        if not text_a or not text_b:
            return 0.0
        tokens_a = set(text_a.split())
        tokens_b = set(text_b.split())
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        return len(intersection) / len(union)

    def _locks_compatible(self, a: Mapping[str, Any], b: Mapping[str, Any]) -> bool:
        locks_a = a.get("authority_locks") or {}
        locks_b = b.get("authority_locks") or {}
        # Compatible if every lock that is True in one is also True in the other
        # (i.e., neither gains new authority)
        for k, v in locks_a.items():
            if v is True and locks_b.get(k) is not True:
                return False
        for k, v in locks_b.items():
            if v is True and locks_a.get(k) is not True:
                return False
        return True

    def _choose_survivor(self, a: Mapping[str, Any], b: Mapping[str, Any]) -> tuple[str, str]:
        # Prefer the one with a longer / more descriptive purpose as a simple quality proxy
        text_a = a.get("purpose") or a.get("description") or ""
        text_b = b.get("purpose") or b.get("description") or ""
        if len(text_a) >= len(text_b):
            return str(a.get("id", "unknown")), str(b.get("id", "unknown"))
        return str(b.get("id", "unknown")), str(a.get("id", "unknown"))


# Dry-run example
if __name__ == "__main__":
    gen = RuneBindMergeCandidateGenerator()
    sample_runes = [
        {"id": "RUNE.A", "purpose": "shadow replay for proposals"},
        {"id": "RUNE.B", "purpose": "execute shadow replay of improvement proposals"},
        {"id": "RUNE.C", "purpose": "meta gate routing"},
    ]
    receipt = gen.propose_candidates(sample_runes, similarity_threshold=0.3)
    print(json.dumps(receipt, indent=2))
