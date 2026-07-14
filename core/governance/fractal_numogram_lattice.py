from __future__ import annotations

from typing import Any

from core.canonical.json import canonical_hash
from core.scoring.mfdfa_hurst import build_mfdfa_hurst_fixture_result


NUMOGRAM_ZONE_BINDINGS = (
    {
        "zone_id": "zone_01_observe",
        "paths": ["docs/atlas/abx-runes.md"],
        "role": "numogram_observe_anchor",
    },
    {
        "zone_id": "zone_02_bind",
        "paths": ["docs/media/abx-runes.svg"],
        "role": "numogram_bind_anchor",
    },
    {
        "zone_id": "zone_03_hold",
        "paths": ["docs/status/badges/runes.json"],
        "role": "numogram_hold_anchor",
    },
    {
        "zone_id": "zone_04_weigh",
        "paths": ["core/scoring/brier.py", "core/scoring/mfdfa_hurst.py"],
        "role": "numogram_weigh_brier_mfdfa_anchor",
    },
    {
        "zone_id": "zone_05_seal",
        "paths": ["docs/status/continuity-spine.json"],
        "role": "numogram_seal_continuity_anchor",
    },
    {
        "zone_id": "zone_06_recursion",
        "paths": ["PLANS.md"],
        "role": "numogram_recursion_plan_anchor",
    },
    {
        "zone_id": "zone_07_hyperstition",
        "paths": ["contracts/governance/v2_hyperstition_anchor.v1.schema.json"],
        "role": "numogram_hyperstition_anchor",
    },
    {
        "zone_id": "zone_08_signal_forage",
        "paths": [
            "scripts/run_ingest_once.py",
            "scripts/run_oracle_intake.py",
            "out/oracle/",
            "core/ingest/",
        ],
        "role": "numogram_signal_forage_shadow_anchor",
    },
    {
        "zone_id": "zone_09_fractal_core",
        "paths": ["core/governance/brier_provenance.py", "core/governance/fractal_numogram_lattice.py"],
        "role": "numogram_fractal_core_computation_anchor",
    },
)


def build_fractal_numogram_brier_scaling_binding() -> dict[str, Any]:
    mfdfa_fixture = build_mfdfa_hurst_fixture_result()
    return {
        "binding_id": "fractal_numogram_brier_mfdfa_hurst_scaling_binding_001",
        "telemetry_only": True,
        "projection_only": True,
        "mfdfa_hurst_bound": True,
        "fractal_numogram_bound": True,
        "hurst_exponent": mfdfa_fixture["hurst_exponent"],
        "mfdfa_profile": mfdfa_fixture["mfdfa_profile"],
        "brier_decomposition_mode": "MURPHY_AND_YATES",
        "mfdfa_hurst_fixture_hash": mfdfa_fixture["mfdfa_hurst_fixture_hash"],
        "resolution_allowed": False,
        "brier_resolution_authorized": False,
        "fractal_numogram_runtime_authorized": False,
        "live_authority_authorized": False,
        "execution_authority": False,
    }


def build_fractal_numogram_lattice_contract() -> dict[str, Any]:
    mfdfa_fixture = build_mfdfa_hurst_fixture_result()
    brier_binding = build_fractal_numogram_brier_scaling_binding()
    packet: dict[str, Any] = {
        "contract_id": "v2_governance_fractal_numogram_lattice_contract_001",
        "telemetry_only": True,
        "projection_only": True,
        "advisory_only": True,
        "fractal_numogram_lattice_activation_recorded": True,
        "fractal_numogram_lattice_telemetry_only": True,
        "fractal_numogram_runtime_authorized": False,
        "numogram_zone_count": len(NUMOGRAM_ZONE_BINDINGS),
        "numogram_zone_bindings": list(NUMOGRAM_ZONE_BINDINGS),
        "mfdfa_hurst_fixture": mfdfa_fixture,
        "brier_scaling_binding": brier_binding,
        "hurst_exponent": mfdfa_fixture["hurst_exponent"],
        "live_authority_authorized": False,
        "live_hyperstition_activation_authorized": False,
        "execution_authority": False,
        "fractal_numogram_lattice_hash": "",
    }
    packet["fractal_numogram_lattice_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "fractal_numogram_lattice_hash"}
    )
    return packet
