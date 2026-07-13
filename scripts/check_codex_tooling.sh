#!/usr/bin/env bash
set -u

CANONICAL_PROJECT="abraxas-v2-full"
STALE_PROJECT="Users-appliedalchemylabs-Documents-Abraxas-v2.0"
STATUS=0

section() {
  printf "\n## %s\n" "$1"
}

observe() {
  printf "OBSERVED: %s\n" "$1"
}

failure() {
  printf "FAILURES: %s\n" "$1"
  STATUS=1
}

not_computable() {
  printf "NOT_COMPUTABLE: %s\n" "$1"
}

require_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    observe "$cmd=$(command -v "$cmd")"
  else
    failure "$cmd=MISSING"
  fi
}

json_field() {
  local json="$1"
  local filter="$2"
  if command -v jq >/dev/null 2>&1; then
    printf "%s" "$json" | jq -r "$filter"
  else
    printf "NOT_COMPUTABLE"
  fi
}

section "Repository"
if repo_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  observe "repo_root=$repo_root"
else
  failure "git rev-parse --show-toplevel failed"
  repo_root="$(pwd)"
fi

if branch="$(git branch --show-current 2>/dev/null)"; then
  if [ -n "$branch" ]; then
    observe "branch=$branch"
  else
    not_computable "branch=detached_or_unknown"
  fi
else
  failure "git branch --show-current failed"
fi

if head_sha="$(git rev-parse HEAD 2>/dev/null)"; then
  observe "head_sha=$head_sha"
else
  failure "git rev-parse HEAD failed"
fi

if status_short="$(git status --short 2>/dev/null)"; then
  if [ -n "$status_short" ]; then
    observe "git_status_short<<EOF"
    printf "%s\n" "$status_short"
    observe "EOF"
  else
    observe "git_status_short=CLEAN"
  fi
else
  failure "git status --short failed"
fi

section "PATH Tools"
for cmd in rg fd jq yq uv ruff basedpyright ast-grep codebase-memory-mcp gh; do
  require_cmd "$cmd"
done

section "Python Tooling"
if command -v uv >/dev/null 2>&1; then
  if uv_version="$(uv --version 2>/dev/null)"; then
    observe "$uv_version"
  else
    failure "uv --version failed"
  fi
else
  not_computable "uv version unavailable because uv is missing"
fi

if command -v ruff >/dev/null 2>&1; then
  if ruff_version="$(ruff --version 2>/dev/null)"; then
    observe "$ruff_version"
  else
    failure "ruff --version failed"
  fi
else
  not_computable "ruff version unavailable because ruff is missing"
fi

if command -v basedpyright >/dev/null 2>&1; then
  if basedpyright_version="$(basedpyright --version 2>/dev/null)"; then
    observe "$basedpyright_version"
  else
    failure "basedpyright --version failed"
  fi
else
  not_computable "basedpyright version unavailable because basedpyright is missing"
fi

section "Codex MCP"
if command -v codex >/dev/null 2>&1; then
  if mcp_list="$(codex mcp list 2>&1)"; then
    if printf "%s\n" "$mcp_list" | rg -q '(^|[[:space:]])codebase-memory([[:space:]]|$)'; then
      observe "codebase-memory MCP registration visible"
    else
      failure "codebase-memory MCP registration not found"
    fi
  else
    failure "codex mcp list failed: $mcp_list"
  fi
else
  not_computable "codex CLI unavailable; cannot inspect MCP registration"
fi

section "Codebase Memory"
if command -v codebase-memory-mcp >/dev/null 2>&1; then
  if projects_json="$(codebase-memory-mcp cli list_projects 2>/dev/null)"; then
    project_count="$(json_field "$projects_json" '.projects | length')"
    observe "project_count=$project_count"

    stale_nodes="$(json_field "$projects_json" '.projects[]? | select(.name == "'"$STALE_PROJECT"'") | .nodes' | sed -n '1p')"
    if [ -n "$stale_nodes" ] && [ "$stale_nodes" != "NOT_COMPUTABLE" ]; then
      failure "stale Codebase Memory project present project=$STALE_PROJECT nodes=$stale_nodes"
    fi

    project_root="$(json_field "$projects_json" '.projects[]? | select(.name == "'"$CANONICAL_PROJECT"'") | .root_path' | sed -n '1p')"
    project_nodes="$(json_field "$projects_json" '.projects[]? | select(.name == "'"$CANONICAL_PROJECT"'") | .nodes' | sed -n '1p')"
    project_edges="$(json_field "$projects_json" '.projects[]? | select(.name == "'"$CANONICAL_PROJECT"'") | .edges' | sed -n '1p')"
    project_head="$(json_field "$projects_json" '.projects[]? | select(.name == "'"$CANONICAL_PROJECT"'") | .git.head_sha' | sed -n '1p')"

    if [ -n "$project_root" ] && [ "$project_root" != "NOT_COMPUTABLE" ]; then
      observe "project=$CANONICAL_PROJECT root=$project_root nodes=$project_nodes edges=$project_edges head=$project_head"
      if [ "$project_root" != "$repo_root" ]; then
        failure "canonical_project_root_mismatch expected=$repo_root actual=$project_root"
      fi
      if [ "$project_nodes" = "0" ] || [ -z "$project_nodes" ] || [ "$project_edges" = "0" ] || [ -z "$project_edges" ]; then
        failure "canonical_project_degraded nodes=${project_nodes:-NOT_COMPUTABLE} edges=${project_edges:-NOT_COMPUTABLE}"
      fi
    else
      failure "canonical Codebase Memory project missing project=$CANONICAL_PROJECT"
    fi
  else
    failure "codebase-memory-mcp cli list_projects failed"
  fi

  if [ -n "${project_root:-}" ] && [ "$project_root" != "NOT_COMPUTABLE" ]; then
    if index_json="$(codebase-memory-mcp cli index_status --project "$CANONICAL_PROJECT" 2>/dev/null)"; then
      index_status="$(json_field "$index_json" '.status')"
      graph_head="$(json_field "$index_json" '.git.head_sha')"
      nodes="$(json_field "$index_json" '.nodes')"
      edges="$(json_field "$index_json" '.edges')"
      observe "index_status=$index_status nodes=$nodes edges=$edges graph_head=$graph_head"
      if [ "$nodes" = "0" ] || [ "$edges" = "0" ]; then
        failure "live_graph_degraded nodes=$nodes edges=$edges"
      fi
      if [ "${head_sha:-}" = "$graph_head" ]; then
        observe "live_graph_current=true"
      else
        failure "live_graph_current=false head_sha=${head_sha:-NOT_COMPUTABLE} graph_head=$graph_head"
      fi
    else
      failure "codebase-memory-mcp cli index_status failed"
    fi

    if changes_json="$(codebase-memory-mcp cli detect_changes --project "$CANONICAL_PROJECT" 2>/dev/null)"; then
      changed_count="$(json_field "$changes_json" '.changed_count')"
      observe "detect_changes.changed_count=$changed_count"
    else
      failure "codebase-memory-mcp cli detect_changes failed"
    fi
  fi
else
  not_computable "Codebase Memory checks unavailable because codebase-memory-mcp is missing"
fi

section "Persisted Artifact"
artifact_path="$repo_root/.codebase-memory/artifact.json"
graph_path="$repo_root/.codebase-memory/graph.db.zst"
if [ -f "$artifact_path" ] && [ -f "$graph_path" ]; then
  observe "artifact_json=$artifact_path"
  observe "graph_db_zst=$graph_path"
  artifact_json="$(cat "$artifact_path")"
  artifact_commit="$(json_field "$artifact_json" '.commit')"
  artifact_nodes="$(json_field "$artifact_json" '.nodes')"
  artifact_edges="$(json_field "$artifact_json" '.edges')"
  observe "artifact_commit=$artifact_commit"
  observe "artifact_nodes=$artifact_nodes artifact_edges=$artifact_edges"
  if [ "${head_sha:-}" = "$artifact_commit" ]; then
    observe "persisted_artifact_current=true"
  else
    failure "persisted_artifact_current=false head_sha=${head_sha:-NOT_COMPUTABLE} artifact_commit=$artifact_commit"
  fi
  if [ "$artifact_nodes" = "0" ] || [ "$artifact_edges" = "0" ]; then
    failure "persisted_artifact_degraded=true artifact_nodes=$artifact_nodes artifact_edges=$artifact_edges"
  fi
else
  failure "persisted Codebase Memory artifact missing under .codebase-memory"
fi

section "Recommended Repair"
if [ "$STATUS" -eq 0 ]; then
  observe "No repair required."
else
  printf "RECOMMENDED_REPAIR: Review FAILURES above. For Codebase Memory project or artifact drift, run codebase-memory-mcp cli index_repository --repo-path %s --mode full --name %s --persistence true from an environment that can write ~/.cache/codebase-memory-mcp, then verify list_projects, index_status, detect_changes, and nonzero .codebase-memory/artifact.json nodes/edges.\n" "$repo_root" "$CANONICAL_PROJECT"
fi

exit "$STATUS"
