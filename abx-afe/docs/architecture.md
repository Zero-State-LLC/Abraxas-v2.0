# AFE Architecture

AFE runs outside Abraxas as a companion module. It seeds a deterministic episode,
computes bounded descriptive metrics, and emits `AFETracePacket.v1` for SHADOW
diagnostics.

The only allowed bridge is:

```text
AFE -> Agent Trace Intake Layer -> SHADOW diagnostics
```

