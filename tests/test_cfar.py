from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from core.cfar import (
    CFARRoute,
    ConstructStatus,
    VariableClass,
    cfar_route,
)


SCHEMA_PATH = Path("contracts/cfar/construct_packet.v1.schema.json")


def test_undefined_cross_cultural_construct_routes_framework_only() -> None:
    packet = cfar_route(
        "Which country has the highest engagement in auspicious consumption?"
    )

    assert packet.construct == "engagement"
    assert packet.construct_status is ConstructStatus.UNDEFINED
    assert packet.variable_class is VariableClass.LATENT
    assert packet.measurement_equivalence_required is True
    assert packet.route is CFARRoute.FRAMEWORK_ONLY
    assert packet.authority["retrieval_authority"] is False


def test_standardized_observable_query_routes_to_retrieval() -> None:
    packet = cfar_route("Which country had the highest GDP in 2024?")

    assert packet.construct is None
    assert packet.construct_status is ConstructStatus.STANDARDIZED
    assert packet.variable_class is VariableClass.OBSERVABLE
    assert packet.route is CFARRoute.EVIDENCE_RETRIEVAL
    assert packet.authority["retrieval_authority"] is True


def test_explicit_definition_changes_latent_construct_to_hybrid() -> None:
    packet = cfar_route(
        "Compare happiness, defined as mean life-evaluation survey score, by country."
    )

    assert packet.construct == "happiness"
    assert packet.construct_status is ConstructStatus.COMPETING
    assert packet.variable_class is VariableClass.HYBRID
    assert packet.route is CFARRoute.HYPOTHESIS_ONLY


def test_noncomparative_latent_query_can_retrieve_after_disclosure() -> None:
    packet = cfar_route("What are the major theories of social capital?")

    assert packet.construct == "social capital"
    assert packet.route is CFARRoute.EVIDENCE_RETRIEVAL
    assert packet.measurement_equivalence_required is False


def test_packet_is_deterministic() -> None:
    query = "Which culture has the most institutional trust?"

    first = cfar_route(query)
    second = cfar_route(query)

    assert first == second
    assert first.to_canonical_json() == second.to_canonical_json()


def test_packet_validates_against_json_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    packet = cfar_route("Which country is the most resilient?").to_dict()

    validator.validate(packet)


@pytest.mark.parametrize(
    "query",
    [
        "Which country has the highest engagement in auspicious consumption?",
        "Which culture is most modern?",
        "Rank nations by spirituality.",
        "Which society has the strongest identity?",
        "Compare institutional trust across countries.",
        "Which country reported the highest population in 2020?",
    ],
)
def test_golden_cases_never_grant_authority(query: str) -> None:
    packet = cfar_route(query)

    assert packet.authority["truth_assignment"] is False
    assert packet.authority["forecast_routing"] is False
    assert packet.authority["canon_mutation"] is False
    assert packet.authority["execution_authority"] is False
