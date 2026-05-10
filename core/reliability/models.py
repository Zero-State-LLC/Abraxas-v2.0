from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
@dataclass(frozen=True)
class ReliabilityScopeRef: scope_type:str; scope_id:str
@dataclass(frozen=True)
class ReliabilityMetricSnapshot: entry_count:int; mean_brier_score:float; expected_calibration_error:float; mean_probability:float; mean_outcome:float; sample_policy:str; reliability_posture:str
@dataclass(frozen=True)
class ReliabilityRecommendation: recommendation_id:str; recommendation_type:str; description:str; actionability:str; mutation_allowed:bool; operator_review_required:bool
@dataclass(frozen=True)
class ReliabilityAdvisoryPolicy: policy_id:str; min_sample_size:int; threshold_policy:Mapping[str, Any]; mutation_policy:str; routing_policy:str
@dataclass(frozen=True)
class AuthorityRef: authority_type:str; authority_id:str; label:str
@dataclass(frozen=True)
class SourceReliabilityAdvisory:
    schema_version:str; advisory_id:str; input_calibration_ledger_id:str; input_calibration_hash:str; scope_ref:ReliabilityScopeRef; metric_snapshot:ReliabilityMetricSnapshot; recommendations:tuple[ReliabilityRecommendation,...]; advisory_status:str; advisory_policy:ReliabilityAdvisoryPolicy; created_by_lane:str; authority_ref:AuthorityRef|None; mutation_allowed:bool; advisory_hash:str
@dataclass(frozen=True)
class ReliabilityValidationFinding: code:str; severity:str; message:str
@dataclass(frozen=True)
class ReliabilityValidationReport: status:str; findings:tuple[ReliabilityValidationFinding,...]; receipt_hash:str
