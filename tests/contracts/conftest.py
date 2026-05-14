import pytest

from scripts import run_artifact_contract_p2c_d5_operator_decision as d5op
from scripts import run_artifact_contract_p2c_d5_human_approval as d5h


@pytest.fixture(scope="session", autouse=True)
def generate_d5_artifacts() -> None:
    """Generate the P2C-D5 operator-decision and human-approval artifacts.

    These files are listed in .gitignore and therefore absent from a fresh
    checkout.  Any contract test that calls d5h.build() or closure.build()
    will raise FileNotFoundError without them.  Running the two upstream
    scripts here — once per test session — ensures every test in this
    package finds the artifacts it needs.
    """
    d5op.main()
    d5h.main()
