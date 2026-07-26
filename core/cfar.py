"""Construct-First Analytical Reasoning (CFAR).

Deterministic pre-retrieval classification for research questions whose answer
may depend on an undefined, latent, or culturally variant construct.

This module is advisory-only. It does not retrieve evidence, assign truth,
promote canon, or grant FORECAST/execution authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ConstructStatus(StrEnum):
    STANDARDIZED = "STANDARDIZED"
    COMPETING = "COMPETING"
    EMERGENT = "EMERGENT"
    UNDEFINED = "UNDEFINED"


class VariableClass(StrEnum):
    OBSERVABLE = "OBSERVABLE"
    LATENT = "LATENT"
    HYBRID = "HYBRID"


class CFARRoute(StrEnum):
    EVIDENCE_RETRIEVAL = "EVIDENCE_RETRIEVAL"
    FRAMEWORK_ONLY = "FRAMEWORK_ONLY"
    HYPOTHESIS_ONLY = "HYPOTHESIS_ONLY"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


@dataclass(frozen=True, slots=True)
class ConstructPacket:
    schema_version: str
    object_id: str
    input_hash: str
    lane: str
    status: str
    provenance: tuple[str, ...]
    query: str
    construct: str | None
    construct_status: ConstructStatus
    variable_class: VariableClass
    dimensions: tuple[str, ...]
    assumptions: tuple[str, ...]
    abstraction_level: int
    measurement_equivalence_required: bool
    route: CFARRoute
    rationale: tuple[str, ...]
    authority: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-native representation that validates against the schema."""
        return {
            "schema_version": self.schema_version,
            "object_id": self.object_id,
            "input_hash": self.input_hash,
            "lane": self.lane,
            "status": self.status,
            "provenance": list(self.provenance),
            "query": self.query,
            "construct": self.construct,
            "construct_status": self.construct_status.value,
            "variable_class": self.variable_class.value,
            "dimensions": list(self.dimensions),
            "assumptions": list(self.assumptions),
            "abstraction_level": self.abstraction_level,
            "measurement_equivalence_required": self.measurement_equivalence_required,
            "route": self.route.value,
            "rationale": list(self.rationale),
            "authority": dict(self.authority),
        }

    def to_canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


_LATENT_TERMS = {
    "auspiciousness",
    "happiness",
    "trust",
    "resilience",
    "corruption",
    "intelligence",
    "culture",
    "meaning",
    "identity",
    "engagement",
    "wellbeing",
    "well-being",
    "social capital",
    "spirituality",
    "modernity",
}
_COMPARATIVE_MARKERS = (
    "which country",
    "which culture",
    "highest",
    "lowest",
    "most ",
    "least ",
    "compare",
    "rank",
)
_ABSTRACT_SUFFIXES = ("ness", "ity", "ism", "tion", "ence", "ance")


def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _candidate_construct(query: str) -> str | None:
    normalized = _normalize(query)
    for term in sorted(_LATENT_TERMS, key=len, reverse=True):
        if term in normalized:
            return term

    words = re.findall(r"[a-z][a-z-]+", normalized)
    for word in words:
        if len(word) > 6 and word.endswith(_ABSTRACT_SUFFIXES):
            return word
    return None


def detect_construct(query: str) -> str | None:
    """Return the most salient construct candidate, if one is detectable."""
    return _candidate_construct(query)


def classify_construct(
    query: str, construct: str | None
) -> tuple[ConstructStatus, VariableClass]:
    """Classify construct status and observability without external retrieval."""
    normalized = _normalize(query)
    if construct is None:
        return ConstructStatus.STANDARDIZED, VariableClass.OBSERVABLE
    if construct in _LATENT_TERMS:
        if "defined as" in normalized or "using the index" in normalized:
            return ConstructStatus.COMPETING, VariableClass.HYBRID
        return ConstructStatus.UNDEFINED, VariableClass.LATENT
    return ConstructStatus.EMERGENT, VariableClass.HYBRID


def decompose_construct(construct: str | None) -> tuple[str, ...]:
    """Emit conservative dimensions for known latent constructs."""
    if construct is None:
        return ()
    known: dict[str, tuple[str, ...]] = {
        "auspiciousness": (
            "belief",
            "symbolic value",
            "timing",
            "institutional embedding",
        ),
        "engagement": ("frequency", "intensity", "duration", "population reach"),
        "happiness": ("affect", "life evaluation", "meaning", "social conditions"),
        "trust": ("interpersonal", "institutional", "behavioral", "declared"),
        "resilience": ("capacity", "adaptation", "recovery", "transformation"),
        "culture": ("practice", "symbol", "institution", "transmission"),
        "identity": (
            "self-concept",
            "social role",
            "affiliation",
            "phase continuity",
        ),
    }
    return known.get(
        construct,
        ("definition", "participation", "institutionalization", "outcome"),
    )


def cfar_route(query: str) -> ConstructPacket:
    """Run deterministic CFAR classification and return a provenance-bound packet."""
    normalized = _normalize(query)
    construct = detect_construct(query)
    construct_status, variable_class = classify_construct(query, construct)
    dimensions = decompose_construct(construct)
    comparative = any(marker in normalized for marker in _COMPARATIVE_MARKERS)

    assumptions: list[str] = []
    rationale: list[str] = []
    if construct is not None:
        assumptions.append(
            "The detected term is treated as the primary analytical construct."
        )
        rationale.append(
            "A non-directly-observable or culturally variant construct was detected."
        )
    if comparative:
        assumptions.append(
            "Comparison requires equivalent indicators across compared units."
        )
        rationale.append("The query requests ranking or cross-context comparison.")

    measurement_equivalence_required = (
        comparative and variable_class != VariableClass.OBSERVABLE
    )
    if construct_status == ConstructStatus.UNDEFINED and comparative:
        route = CFARRoute.FRAMEWORK_ONLY
        rationale.append(
            "Retrieval before operationalization would create a hidden-definition ranking."
        )
    elif (
        construct_status in {ConstructStatus.COMPETING, ConstructStatus.EMERGENT}
        and comparative
    ):
        route = CFARRoute.HYPOTHESIS_ONLY
        rationale.append(
            "Competing definitions permit bounded hypotheses, not a definitive rank."
        )
    else:
        route = CFARRoute.EVIDENCE_RETRIEVAL
        rationale.append("The construct is sufficiently bounded for evidence retrieval.")

    abstraction_level = 3 if measurement_equivalence_required else (2 if construct else 1)
    input_hash = _hash(normalized)
    object_id = f"cfar-{input_hash[:16]}"
    return ConstructPacket(
        schema_version="cfar.v1",
        object_id=object_id,
        input_hash=input_hash,
        lane="SHADOW",
        status="VALID",
        provenance=("USER_QUERY", "CFAR_DETERMINISTIC_HEURISTIC_V1"),
        query=query.strip(),
        construct=construct,
        construct_status=construct_status,
        variable_class=variable_class,
        dimensions=dimensions,
        assumptions=tuple(assumptions),
        abstraction_level=abstraction_level,
        measurement_equivalence_required=measurement_equivalence_required,
        route=route,
        rationale=tuple(rationale),
        authority={
            "truth_assignment": False,
            "forecast_routing": False,
            "canon_mutation": False,
            "execution_authority": False,
            "retrieval_authority": route == CFARRoute.EVIDENCE_RETRIEVAL,
        },
    )
