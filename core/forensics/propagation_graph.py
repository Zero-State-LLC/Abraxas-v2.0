"""PropagationGraph.v0 dry-run from EvidencePack sources/claims. No network."""

from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash

SCHEMA_VERSION = "PropagationGraph.v0"
DEFAULT_AUTHORITY = {
    "execution_authority": False,
    "promotion_authorized": False,
    "forecast_routing_authorized": False,
    "canon_mutation_allowed": False,
    "publish_authorized": False,
}


def build_propagation_graph_from_pack(pack: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(pack, Mapping):
        body = {
            "schema_version": SCHEMA_VERSION,
            "pack_id": "",
            "nodes": [],
            "edges": [],
            "node_count": 0,
            "edge_count": 0,
            "write_performed": False,
            "network_calls": False,
            "authority": dict(DEFAULT_AUTHORITY),
            "advisory_only": True,
            "lane": "SHADOW",
        }
        body["canonical_hash"] = canonical_hash(body)
        return body

    pack_id = str(pack.get("pack_id") or "")
    sources = pack.get("sources") if isinstance(pack.get("sources"), list) else []
    claims = pack.get("claims") if isinstance(pack.get("claims"), list) else []
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    source_ids: list[str] = []

    for src in sources:
        if not isinstance(src, dict):
            continue
        sid = str(src.get("source_id") or "")
        if not sid:
            continue
        source_ids.append(sid)
        nodes.append(
            {
                "node_id": f"src:{sid}",
                "kind": "source",
                "register": "OBSERVED",
                "label": str(src.get("title") or sid)[:200],
            }
        )

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        cid = str(claim.get("claim_id") or claim.get("id") or "")
        if not cid:
            continue
        reg = str(claim.get("register") or "NOT_COMPUTABLE")
        nodes.append(
            {
                "node_id": f"meme:{cid}",
                "kind": "meme_unit",
                "register": reg,
                "label": str(claim.get("text") or claim.get("claim_text") or cid)[:200],
            }
        )
        kind = (
            "observed_cite"
            if reg == "OBSERVED"
            else "inferred_echo"
            if reg == "INFERRED"
            else "speculative_spread"
        )
        refs = claim.get("source_ids") or claim.get("sources") or []
        if isinstance(refs, list) and refs:
            for ref in refs[:8]:
                edges.append(
                    {
                        "from_id": f"src:{ref}",
                        "to_id": f"meme:{cid}",
                        "kind": kind,
                    }
                )
        elif source_ids:
            edges.append(
                {
                    "from_id": f"src:{source_ids[0]}",
                    "to_id": f"meme:{cid}",
                    "kind": kind,
                }
            )

    fixed_edges = []
    for i, e in enumerate(
        sorted(edges, key=lambda x: (x["from_id"], x["to_id"], x["kind"]))
    ):
        fixed = dict(e)
        fixed["edge_id"] = f"e:{fixed['from_id']}:{fixed['to_id']}:{fixed['kind']}:{i}"
        fixed_edges.append(fixed)

    nodes_sorted = sorted(nodes, key=lambda n: n["node_id"])
    edges_sorted = sorted(fixed_edges, key=lambda e: e["edge_id"])
    body = {
        "schema_version": SCHEMA_VERSION,
        "pack_id": pack_id,
        "nodes": nodes_sorted,
        "edges": edges_sorted,
        "node_count": len(nodes_sorted),
        "edge_count": len(edges_sorted),
        "write_performed": False,
        "network_calls": False,
        "authority": dict(DEFAULT_AUTHORITY),
        "advisory_only": True,
        "lane": "SHADOW",
    }
    body["canonical_hash"] = canonical_hash(body)
    return body
