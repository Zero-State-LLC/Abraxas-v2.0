#!/usr/bin/env python3
"""
Thin ALife Adapter for abx-esoteric-intelligence.

Provides pure functions to build ALife-compatible packets from esoteric analysis.
Used by runner and future integrations. No runtime, no authority claims.
All outputs are SHADOW, with entity_assertion=false, forecast_authority=false, etc.

KISS: deterministic, no side effects, stable ordering.
"""

from __future__ import annotations
import hashlib
from typing import Any, Dict
from functools import wraps


def synthetic_only(builder):
    """Legacy canned builders are fixtures, never observational adapters."""
    @wraps(builder)
    def wrapped(input_data, request):
        if request.get("synthetic_fixture") is not True:
            raise ValueError("NOT_COMPUTABLE: adapter is a synthetic fixture; explicit opt-in required")
        packet = builder(input_data, request)
        packet["synthetic"] = True
        packet["evidence_status"] = "SYNTHETIC"
        return packet
    return wrapped


def _provenance_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


@synthetic_only
def build_organism_candidate(input_data: str, request: Dict[str, Any]) -> Dict[str, Any]:
    """Build SymbolicOrganismCandidate.v1 for handoff to existing ALife runtime."""
    text = input_data or "Sample symbolic structure"
    candidate_id = f"SYMORG-{_provenance_hash(text).upper()[:8]}"
    organism_class = (
        "HYPERSTITION" if "hyperstition" in text.lower()
        else "ARCHETYPE" if "archetype" in text.lower()
        else "SYMBOL"
    )
    return {
        "schema_version": "ABX.SymbolicOrganismCandidate.v1",
        "candidate_id": candidate_id,
        "source_analysis_packet_id": request.get("request_id", "unknown"),
        "organism_class": organism_class,
        "genotype": {
            "canonical_features": (
                ["threshold", "transformation", "guide"]
                if "door" in text.lower() or "water" in text.lower()
                else ["symbolic-structure"]
            ),
            "source_traditions": ["dream_unconscious_symbol"],
            "motif_signature": ["liminality"],
            "correspondence_signature": [],
            "transformation_rules": ["initiation"],
            "compatible_runes": ["RUNE.DREAM.MOTIF.TRACE"],
            "provenance_hash": _provenance_hash(text),
        },
        "phenotype": {
            "observed_expressions": [text[:80]],
            "media_forms": [],
            "ritual_forms": [],
            "cultural_expressions": [],
            "computational_outputs": [],
        },
        "environment": {
            "source_corpora": ["dream_unconscious_symbol"],
            "habitats": ["NOCTIS", "SYMBOLIC_CORPUS"],
            "niches": ["threshold"],
            "pressure_fields": [],
            "operator_context_refs": [],
        },
        "fitness_inputs": {
            "recurrence": 0.58,
            "cross_domain_reuse": 0.42,
            "interpretive_utility": 0.71,
            "stability": 0.49,
            "novelty": 0.53,
            "provenance_strength": 0.38,
            "drift_risk": 0.32,
        },
        "lineage": {
            "historical_ancestors": [],
            "modern_derivatives": [],
            "operator_variants": [],
            "mutations": [],
            "syncretic_crossings": [],
        },
        "governance": {
            "lane": "SHADOW",
            "entity_assertion": False,
            "causal_authority": False,
            "truth_authority": False,
            "forecast_authority": False,
            "execution_authority": False,
        },
    }


@synthetic_only
def build_archetype_lineage(input_data: str, request: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": "ABX.ArchetypeLineage.v1",
        "source": input_data,
        "earliest_sourced_forms": ["Hermes (Greek)"],
        "tradition_branches": ["Hermes -> Mercurius (alchemical)", "modern trickster"],
        "stable_motif_genes": ["messenger", "threshold", "guide"],
        "acquired_motifs": ["computational agent"],
        "lost_motifs": [],
        "current_phenotypes": ["esoteric skill adapter"],
        "active_habitats": ["SYMBOLIC_CORPUS", "NOCTIS"],
        "drift_risk": 0.3,
        "governance": {"lane": "SHADOW", "entity_assertion": False},
    }


@synthetic_only
def build_sigil_genotype(input_data: str, request: Dict[str, Any]) -> Dict[str, Any]:
    text = input_data or ""
    return {
        "schema_version": "ABX.SigilGenotype.v1",
        "genotype": {
            "source_text": text,
            "construction": "letter_elimination",
            "primitives": ["H", "M"],
            "provenance_hash": _provenance_hash(text),
        },
        "phenotype_variants": ["rendered_glyph", "ABX_variant"],
        "variant_classification": "OPERATOR_DERIVATIVE",
        "governance": {"entity_assertion": False},
    }


@synthetic_only
def build_population_model(input_data: str, request: Dict[str, Any]) -> Dict[str, Any]:
    text = input_data or ""
    return {
        "schema_version": "ABX.DistributedSymbolicPopulation.v1",
        "population_id": f"POP-{_provenance_hash(text).upper()[:8]}",
        "population_class": "HYPERSTITION",
        "core_genotype": {"motifs": ["messenger"], "claims": ["symbolic persistence"]},
        "habitats": ["SYMBOLIC_CORPUS", "AAL_VIZ"],
        "propagation_channels": ["operator_input", "esoteric_analysis"],
        "mutation_rate": 0.12,
        "coherence": 0.68,
        "population_persistence": 0.55,
        "entity_assertion": False,
        "causal_claim": False,
    }


@synthetic_only
def build_metabolism_packet(input_data: str, request: Dict[str, Any]) -> Dict[str, Any]:
    text = input_data or ""
    return {
        "schema_version": "ABX.SymbolicMetabolismPacket.v1",
        "packet_id": f"META-{_provenance_hash(text).upper()[:8]}",
        "input_primitives": ["symbol", "intent"],
        "admitted_symbols": ["threshold", "guide"],
        "reaction_sequence": ["intake", "transformation", "integration"],
        "catalysts": ["operator_context"],
        "transformation_products": ["adapted_symbolic_organism"],
        "unresolved_residues": [],
        "toxic_byproducts": [],
        "closure_status": "CLOSED",
        "provenance": {"source": "esoteric_analysis"},
        "execution_claimed": False,
    }


@synthetic_only
def build_synchronicity_ecology(input_data: str, request: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": "ABX.SynchronicityAnalysisPacket.v1",
        "alife_ecology": {
            "candidate_organisms": ["messenger_archetype"],
            "habitats": ["SYMBOLIC_CORPUS"],
            "propagation_paths": ["operator_input"],
            "exposure_events": [],
            "selection_events": ["attention"],
            "attention_reinforcement": ["recurrence"],
            "mutation_events": [],
            "environmental_coupling_score": 0.55,
        },
        "governance": {"lane": "SHADOW", "forecast_authority": False},
    }


# Mapping for runner dispatch
ALIFE_MODE_BUILDERS = {
    "organismize": build_organism_candidate,
    "archetype_lineage": build_archetype_lineage,
    "sigil_genotype": build_sigil_genotype,
    "population_model": build_population_model,
    "metabolism": build_metabolism_packet,
    "synchronicity_ecology": build_synchronicity_ecology,
}


def build_alife_packet(mode: str, input_data: str, request: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch to the correct builder. Raises KeyError for unknown ALife mode."""
    builder = ALIFE_MODE_BUILDERS[mode]
    return builder(input_data, request)
