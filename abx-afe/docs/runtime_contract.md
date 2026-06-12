# Runtime Contract

`RUNE.AFE_TRACE` accepts a deterministic simulation episode and emits
`AFETracePacket.v1`.

Missing `agent_id`, `environment_id`, `episode_id`, or provenance input hash
returns `NOT_COMPUTABLE`.

