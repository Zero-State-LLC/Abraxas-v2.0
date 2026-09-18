"""Abraxas-side Sigil-Forge bridge.

Agent-agnostic: resolve the standalone engine via SIGIL_FORGE_* env, a
checkout, or ~/.sigil-forge. Hermes paths are last-compat only. Never
smash-merge forge scripts into this repo. Never invent primitives.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

_VOWELS = set("aeiouy")
_NATIVE_ROOT_ENV = (
    "SIGIL_FORGE_HOME",
    "SIGIL_FORGE_ROOT",
    "SIGIL_FORGE_DIR",
    "SIGIL_FORGE_SKILL_DIR",
)
_DISCOVERY_SOURCE = "none"


def normalize_intent(text: str) -> str:
    if text is None:
        raise ValueError("intent is required")
    s = unicodedata.normalize("NFKC", str(text))
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    if not s:
        raise ValueError("intent is empty after normalization")
    return s


def letter_sequence(normalized: str) -> List[str]:
    """Spare letter_monogram: a–z, strip vowels, unique first-seen."""
    chars = re.findall(r"[a-z]", normalized.lower())
    out: List[str] = []
    seen: set[str] = set()
    for ch in chars:
        if ch in _VOWELS or ch in seen:
            continue
        seen.add(ch)
        out.append(ch)
    return out


def intent_digest(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _scripts_under(root: Path) -> Path:
    return root / "scripts" if root.name != "scripts" else root


def engine_script_dirs() -> List[Path]:
    """Ordered engine roots. Native env first; Hermes last."""
    dirs: List[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        try:
            resolved = path.expanduser().resolve()
        except OSError:
            return
        if resolved in seen:
            return
        seen.add(resolved)
        dirs.append(resolved)

    for key in _NATIVE_ROOT_ENV:
        raw = os.environ.get(key)
        if raw:
            add(_scripts_under(Path(raw)))

    # Checkouts / default native install (no Hermes required)
    add(Path.home() / "Sigil-Forge" / "scripts")
    add(Path.home() / ".sigil-forge" / "scripts")
    here = Path(__file__).resolve()
    for parent in here.parents:
        add(parent / "Sigil-Forge" / "scripts")

    # Optional Hermes compatibility — never the identity of the engine
    raw = os.environ.get("HERMES_SKILL_DIR")
    if raw:
        add(_scripts_under(Path(raw)))
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        add(Path(hermes_home) / "skills" / "sigil-forge" / "scripts")
    add(Path.home() / ".hermes" / "skills" / "sigil-forge" / "scripts")
    return dirs


def configured_discovery_label() -> str:
    for key in _NATIVE_ROOT_ENV:
        if os.environ.get(key):
            return f"env:{key}"
    if os.environ.get("HERMES_SKILL_DIR") or os.environ.get("HERMES_HOME"):
        return "compat:hermes"
    return "search"


def discovery_source() -> str:
    return _DISCOVERY_SOURCE if _DISCOVERY_SOURCE != "none" else configured_discovery_label()


def load_forge_core() -> Optional[Any]:
    global _DISCOVERY_SOURCE
    _DISCOVERY_SOURCE = "none"
    for scripts in engine_script_dirs():
        core = scripts / "forge_core.py"
        if not core.is_file():
            continue
        scripts_str = str(scripts)
        if scripts_str not in sys.path:
            sys.path.insert(0, scripts_str)
        try:
            import forge_core  # type: ignore
        except Exception:
            continue
        label = None
        for key in _NATIVE_ROOT_ENV:
            raw = os.environ.get(key)
            if not raw:
                continue
            try:
                if scripts == _scripts_under(Path(raw)).expanduser().resolve():
                    label = f"env:{key}"
                    break
            except OSError:
                continue
        if label is None:
            if "hermes" in scripts_str.lower():
                label = "compat:hermes"
            else:
                label = "checkout"
        _DISCOVERY_SOURCE = label
        return forge_core
    return None


def compute_genotype_core(text: str) -> Dict[str, Any]:
    """Return engine-labeled genotype internals (no authority grants)."""
    normalized = normalize_intent(text)
    digest = intent_digest(normalized)
    engine = "local_spare_reduction"
    variant = "LOCAL_SPARE_REDUCTION"
    square_name = None
    square_order = None
    forge = load_forge_core()
    if forge is not None:
        try:
            cfg = forge.ForgeConfig(mode="creative", spare_mode="letter_monogram")
            result = forge.compute_forge(normalized, cfg)
            primitives = list(result.spare_letters)
            digest = result.intent_digest
            engine = "sigil-forge"
            variant = "FORGE_CORE"
            square_name = result.square_name
            square_order = result.square_order
            if not primitives:
                return {
                    "normalized": normalized,
                    "intent_digest": digest,
                    "primitives": [],
                    "construction": "NOT_COMPUTABLE",
                    "engine": engine,
                    "variant_classification": variant,
                    "claim_class": "NOT_COMPUTABLE",
                    "reason": "NOT_COMPUTABLE: no surviving Spare consonants",
                    "square_name": square_name,
                    "square_order": square_order,
                    "discovery": discovery_source(),
                }
            return {
                "normalized": normalized,
                "intent_digest": digest,
                "primitives": primitives,
                "construction": "spare.letter_monogram",
                "engine": engine,
                "variant_classification": variant,
                "claim_class": "COMPUTED",
                "reason": None,
                "square_name": square_name,
                "square_order": square_order,
                "discovery": discovery_source(),
            }
        except ValueError as exc:
            msg = str(exc)
            if "NOT_COMPUTABLE" in msg:
                return {
                    "normalized": normalized,
                    "intent_digest": digest,
                    "primitives": [],
                    "construction": "NOT_COMPUTABLE",
                    "engine": "sigil-forge",
                    "variant_classification": "FORGE_CORE",
                    "claim_class": "NOT_COMPUTABLE",
                    "reason": msg,
                    "square_name": None,
                    "square_order": None,
                    "discovery": discovery_source(),
                }
            raise

    primitives = letter_sequence(normalized)
    payload = {
        "normalized": normalized,
        "intent_digest": digest,
        "primitives": primitives,
        "engine": engine,
        "variant_classification": variant,
        "square_name": square_name,
        "square_order": square_order,
        "discovery": "local_spare_reduction",
    }
    if not primitives:
        payload.update(
            {
                "construction": "NOT_COMPUTABLE",
                "claim_class": "NOT_COMPUTABLE",
                "reason": "NOT_COMPUTABLE: no surviving Spare consonants",
            }
        )
        return payload
    payload.update(
        {
            "construction": "spare.letter_monogram",
            "claim_class": "COMPUTED",
            "reason": None,
        }
    )
    return payload


def default_governance() -> Dict[str, Any]:
    return {
        "lane": "SHADOW",
        "entity_assertion": False,
        "causal_authority": False,
        "truth_authority": False,
        "forecast_authority": False,
        "execution_authority": False,
        "canon_authority": False,
    }
