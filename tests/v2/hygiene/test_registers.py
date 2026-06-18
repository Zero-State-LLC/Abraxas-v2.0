from abraxas.v2.hygiene.registers import V2Output


def test_v2_output_is_valid_with_observed_register() -> None:
    output = V2Output(observed={"a": 1}, inferred={}, speculative={})
    assert output.is_valid()


def test_v2_output_requires_register_content() -> None:
    try:
        V2Output(observed={}, inferred={}, speculative={})
        raised = False
    except ValueError:
        raised = True
    assert raised
