import tomllib
from pathlib import Path


def test_wheel_includes_supported_runtime_and_contract_assets():
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    wheel = config["tool"]["hatch"]["build"]["targets"]["wheel"]
    assert wheel["packages"] == ["abraxas", "core"]
    assert wheel["force-include"]["contracts"] == "contracts"


def test_instantiation_contract_assets_exist_for_packaged_validators():
    expected = {
        "instantiation_state.v1.schema.json",
        "instantiation_transition.v1.schema.json",
        "intervention_declaration.v1.schema.json",
    }
    actual = {
        path.name
        for path in Path("contracts/instantiation").glob("*.schema.json")
    }
    assert expected <= actual
