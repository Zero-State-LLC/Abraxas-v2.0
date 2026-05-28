---
name: P102 stabilization window monitor observations path
description: How to unblock P102 stabilization window monitor from CONTINUE loop
---
`run_research_stabilization_window_monitor.py` needs `--observations-path input/research_stabilization_window_observations.json` to avoid CONTINUE loop (window_complete_candidates: []).

**Fix:** `python scripts/run_research_stabilization_window_monitor.py --observations-path input/research_stabilization_window_observations.json`

**Why:** Without observations, all candidate windows show zero complete cycles → CONTINUE → P103 blocked.

**How to apply:** Whenever the stabilization window monitor is run as part of a research fold path (P94_research_fold → P101 → P102), always supply the observations path.
