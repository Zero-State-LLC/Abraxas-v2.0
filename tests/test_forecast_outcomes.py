from core.forecast.outcomes import ForecastOutcomeBindingPacket


def test_unresolved_bindings_allowed() -> None:
    p = ForecastOutcomeBindingPacket(binding_id="b", forecast_hash="f", expected_outcome_hash="h")
    assert p.binding_status == "unresolved"
