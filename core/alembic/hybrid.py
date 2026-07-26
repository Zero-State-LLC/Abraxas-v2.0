"""Hybrid plan construction and validation."""

from __future__ import annotations

from core.alembic.models import HybridNode, HybridPlan
from core.alembic.util import make_id


def validate_hybrid_plan(plan: HybridPlan) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    node_ids = {node.node_id for node in plan.nodes}
    if len(node_ids) != len(plan.nodes):
        reasons.append("duplicate_node_ids")
    for node in plan.nodes:
        for dep in node.depends_on:
            if dep not in node_ids:
                reasons.append(f"missing_dependency:{node.node_id}->{dep}")
    # Cycle detection (reject unless bounded iterative loop explicitly set).
    adjacency = {node.node_id: set(node.depends_on) for node in plan.nodes}
    visiting: set[str] = set()
    visited: set[str] = set()

    def _dfs(node_id: str) -> bool:
        if node_id in visiting:
            return True
        if node_id in visited:
            return False
        visiting.add(node_id)
        for dep in adjacency.get(node_id, set()):
            if _dfs(dep):
                return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    cyclic = any(_dfs(node_id) for node_id in node_ids)
    if cyclic and plan.iterative_loop_bound is None:
        reasons.append("cycle_without_bounded_iterative_loop")
    if plan.execution_order and set(plan.execution_order) != node_ids:
        reasons.append("execution_order_mismatch")
    return (not reasons, tuple(reasons))


def build_hybrid_plan(
    selected_architecture_ids: tuple[str, ...],
    *,
    family_by_id: dict[str, str],
    fusion_method: str,
) -> HybridPlan | None:
    if len(selected_architecture_ids) < 2:
        return None
    nodes: list[HybridNode] = []
    order: list[str] = []
    # Prefer symbolic/operator verification after specialists.
    specialists = [
        arch_id
        for arch_id in selected_architecture_ids
        if family_by_id.get(arch_id) not in {"symbolic_expert", "human_operator_review"}
    ]
    verifiers = [
        arch_id
        for arch_id in selected_architecture_ids
        if family_by_id.get(arch_id) in {"symbolic_expert", "human_operator_review"}
    ]
    ordered = specialists + verifiers
    if not ordered:
        ordered = list(selected_architecture_ids)
    previous: str | None = None
    for index, architecture_id in enumerate(ordered):
        node_id = f"node-{index}-{architecture_id}"
        depends = (previous,) if previous is not None else ()
        role = "verify" if family_by_id.get(architecture_id) == "symbolic_expert" else "contribute"
        if family_by_id.get(architecture_id) == "human_operator_review":
            role = "operator_review"
        nodes.append(
            HybridNode(
                node_id=node_id,
                architecture_id=architecture_id,
                role=role,
                depends_on=depends,
            )
        )
        order.append(node_id)
        previous = node_id
    plan = HybridPlan(
        plan_id=make_id("hybrid", *ordered),
        nodes=tuple(nodes),
        execution_order=tuple(order),
        parallelizable_stages=tuple((node.node_id,) for node in nodes),
        verification_points=tuple(
            node.node_id for node in nodes if node.role in {"verify", "operator_review"}
        ),
        stop_conditions=("verification_fail", "adapter_unavailable"),
        fallbacks=("abstain",),
        fusion_method=fusion_method,
    )
    ok, reasons = validate_hybrid_plan(plan)
    if not ok:
        raise ValueError(f"invalid hybrid plan: {reasons}")
    return plan
