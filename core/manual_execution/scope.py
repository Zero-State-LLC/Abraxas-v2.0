from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED_REVIEW_ACTIONS = {"inspect","compare","document","request_changes","defer","deny"}
FORBIDDEN_ACTIONS = {"execute","activate","deploy","route_production","mutate_forecast","mutate_weight","mutate_canon"}

class ManualExecutionScopePacket(BaseModel):
    schema_version: Literal["ManualExecutionScopePacket.v1"] = "ManualExecutionScopePacket.v1"
    scope_id: str
    overlay_hash: str
    allowed_review_actions: list[str]
    forbidden_actions: list[str]
    scope_constraints: list[str]
    deterministic_scope_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:list[str],c:list[str],d:list[str])->str:
        return hashlib.sha256(f"{a}|{'|'.join(sorted(b))}|{'|'.join(sorted(c))}|{'|'.join(sorted(d))}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self):
        self.authority.assert_locked()
        if any(a not in ALLOWED_REVIEW_ACTIONS for a in self.allowed_review_actions):
            raise ValueError('invalid allowed action')
        if set(self.forbidden_actions) != FORBIDDEN_ACTIONS:
            raise ValueError('forbidden actions must be explicit')
        if any(a in FORBIDDEN_ACTIONS for a in self.allowed_review_actions):
            raise ValueError('forbidden action allowed')
        if self.deterministic_scope_hash != self.compute_hash(self.overlay_hash,self.allowed_review_actions,self.forbidden_actions,self.scope_constraints):
            raise ValueError('scope hash')
        return self
