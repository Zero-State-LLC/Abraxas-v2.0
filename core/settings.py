"""Typed runtime settings root (separate from RuntimePaths path catalog).

Domain modules must not read environment variables at import time. Call
``load_runtime_settings()`` / ``configure_runtime_settings()`` explicitly from
CLI, API factory, or tests.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.config import RuntimePaths
from core.governance.activation_evidence import (
    EvidenceVerification,
    verify_evidence_files,
)
from core.governance.activation_policy import ActivationLane


class RuntimeSettings(BaseSettings):
    """Application settings: activation, layout roots, and feature flags."""

    model_config = SettingsConfigDict(
        env_prefix="ABRAXAS_",
        extra="ignore",
        frozen=True,
    )

    app_title: str = "ABRAXAS v2"
    # Reference build label, not a product version (docs/releases/VERSION_STRATEGY.md).
    app_version: str = "0.0.0+reference"
    default_activation_lane: ActivationLane = ActivationLane.LOCAL_DEV
    repo_root: Path = Field(default_factory=lambda: Path.cwd())
    contracts_dir: Path = Path("contracts")
    out_dir: Path = Path("out")
    require_classified_artifact_writes: bool = False
    enable_analyze_endpoint: bool = True
    require_public_readonly_for_analyze: bool = False
    # POST /analyze access policy (apps/api/boundaries.py). Authenticated by
    # default; anonymous only for local development on a loopback client.
    api_token: SecretStr | None = None
    deployment_profile: Literal["local", "deployed"] = "deployed"
    allow_anonymous_local_dev: bool = False
    analyze_rate_limit_per_minute: int = Field(default=30, ge=1)
    max_request_bytes: int = Field(default=262_144, ge=1024)
    analyze_timeout_seconds: float = Field(default=10.0, gt=0)
    # INTERNAL_CANARY evidence (core/governance/activation_evidence.py). Set by
    # the deployment, never by the candidate: evidence + trust store files and
    # the revision/config the deployment is activating.
    canary_evidence_path: Path | None = None
    canary_trust_store_path: Path | None = None
    candidate_revision: str | None = None
    candidate_config_digest: str | None = None
    # Provider invoke gate (FixtureProvider / future adapters). Default deny.
    allow_provider_invoke: bool = False

    @field_validator("default_activation_lane", mode="before")
    @classmethod
    def _lane(cls, value: Any) -> Any:
        if isinstance(value, ActivationLane):
            return value
        return ActivationLane(str(value))

    @model_validator(mode="after")
    def _anonymous_only_in_local_profile(self) -> RuntimeSettings:
        if self.allow_anonymous_local_dev and self.deployment_profile != "local":
            raise ValueError(
                "ABRAXAS_ALLOW_ANONYMOUS_LOCAL_DEV requires ABRAXAS_DEPLOYMENT_PROFILE=local"
            )
        return self

    @field_validator("repo_root", "contracts_dir", "out_dir", mode="before")
    @classmethod
    def _path(cls, value: Any) -> Path:
        return Path(value)

    def canary_evidence_verification(self, now: datetime | None = None) -> EvidenceVerification:
        """Verify deployment-supplied INTERNAL_CANARY evidence (fail closed)."""
        return verify_evidence_files(
            self.canary_evidence_path,
            self.canary_trust_store_path,
            expected_revision=self.candidate_revision,
            expected_config_digest=self.candidate_config_digest,
            now=now or datetime.now(UTC),
        )

    def resolved_contracts_dir(self) -> Path:
        path = self.contracts_dir
        return path if path.is_absolute() else (self.repo_root / path)

    def resolved_out_dir(self) -> Path:
        path = self.out_dir
        return path if path.is_absolute() else (self.repo_root / path)

    def runtime_paths(self) -> RuntimePaths:
        """Filesystem layout helper; not a DI container for credentials/adapters."""
        return RuntimePaths(
            contracts_dir=self.resolved_contracts_dir(),
            out_dir=self.resolved_out_dir(),
        )

    def redacted_diagnostics(self) -> dict[str, Any]:
        """Safe settings dump for status/diagnostics (no secrets by construction)."""
        return {
            "app_title": self.app_title,
            "app_version": self.app_version,
            "default_activation_lane": self.default_activation_lane.value,
            "repo_root": str(self.repo_root),
            "contracts_dir": str(self.resolved_contracts_dir()),
            "out_dir": str(self.resolved_out_dir()),
            "require_classified_artifact_writes": self.require_classified_artifact_writes,
            "enable_analyze_endpoint": self.enable_analyze_endpoint,
            "require_public_readonly_for_analyze": self.require_public_readonly_for_analyze,
            "api_token_configured": self.api_token is not None,
            "deployment_profile": self.deployment_profile,
            "allow_anonymous_local_dev": self.allow_anonymous_local_dev,
            "analyze_rate_limit_per_minute": self.analyze_rate_limit_per_minute,
            "max_request_bytes": self.max_request_bytes,
            "analyze_timeout_seconds": self.analyze_timeout_seconds,
            "canary_evidence_configured": self.canary_evidence_path is not None,
            "candidate_revision": self.candidate_revision,
            "allow_provider_invoke": self.allow_provider_invoke,
        }


_RUNTIME_SETTINGS: RuntimeSettings | None = None


def load_runtime_settings(**overrides: object) -> RuntimeSettings:
    if overrides:
        return RuntimeSettings(**overrides)  # type: ignore[arg-type]
    return RuntimeSettings()


def configure_runtime_settings(
    settings: RuntimeSettings | None = None,
    **overrides: object,
) -> RuntimeSettings:
    global _RUNTIME_SETTINGS
    if settings is not None and overrides:
        raise ValueError("pass settings or overrides, not both")
    _RUNTIME_SETTINGS = (
        settings if settings is not None else load_runtime_settings(**overrides)
    )
    return _RUNTIME_SETTINGS


def get_runtime_settings() -> RuntimeSettings:
    global _RUNTIME_SETTINGS
    if _RUNTIME_SETTINGS is None:
        _RUNTIME_SETTINGS = load_runtime_settings()
    return _RUNTIME_SETTINGS
