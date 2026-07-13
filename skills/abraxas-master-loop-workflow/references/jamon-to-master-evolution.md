# Jamon → Master Loop Evolution Notes

This master skill evolves `abraxas-jamon-agentic-workflow` (v1.0).

## Key Additions
- Anthropic Loop Engineering: 5 explicit building blocks, generator/evaluator split, loop taxonomy (turn/goal/time/proactive).
- Stronger emphasis on verifiable stop conditions and machine checks.
- Structured LOOP_STATE + NEXT_ACTION in every cycle receipt.
- Explicit "design the loop that prompts you" imperative.

## Migration
- For new autonomous work, load `@/abraxas-master-loop-workflow` as primary.
- The jamon skill remains useful for Jamon-specific 0-18 checklists and as a reference.
- Update related_skills lists to include the master.
- Existing worksheets/receipts from jamon era remain valid; new ones use master format.

See main SKILL.md for full integration. Patch predecessor skill to link here.