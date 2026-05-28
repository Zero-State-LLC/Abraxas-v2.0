---
name: P94 temporal continuity seal dry-run blocker
description: Missing script blocking the main temporal continuity chain at P93→P94
---
The script `scripts/run_temporal_continuity_operator_authorization_record_approval_record_seal_dry_run.py` does not exist. P93 (`run_temporal_continuity_operator_authorization_record_approval_record_seal_plan.py`) always routes to `P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN`.

**Why:** This is the original root blocker for the main temporal continuity chain. It cannot be unblocked by running existing lanes — it requires a new governed script to be introduced through an operator-authorized governance design lane.

**How to apply:** Do not attempt to stub or create this script without an explicit operator authorization. Report it as an operator-facing blocker requiring governance design.
