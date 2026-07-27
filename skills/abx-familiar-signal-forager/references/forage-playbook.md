# Forage playbook (quality bar)

## Good pack

- ≥3 independent sources when the topic is public
- At least one **primary** source (docs, filing, paper, code, official stats)
- Every `must_answer` either answered with register tags or `NOT_COMPUTABLE`
- Excerpts are short and checkable
- Clear non-claims section in the brief

## Bad pack

- "As of my knowledge cutoff…" presented as OBSERVED
- Five blog roundups, zero primaries
- Revenue TAM invented from vibe
- Missing URLs
- SPECULATIVE recommendations without labels

## Worked mini-flow

Topic: "Does project X expose a public API for Y?"

1. `web_search` official docs + GitHub
2. `web_extract` docs page; quote endpoint table → OBSERVED
3. If docs silent, search issues/discussions → secondary OBSERVED
4. If still silent → answer NOT_COMPUTABLE with "no public primary found in forage window"
5. Write pack + brief; do not claim "no API exists" unless exhaustive scope was agreed

## Density heuristic for Neon Genie hand-off

| OBSERVED sources on market claims | Allowed language |
|-----------------------------------|------------------|
| 0 | NOT_COMPUTABLE only |
| 1–2 | Cautious INFERRED; no hard TAM |
| 3+ diversified | Structured market_model fields with citations |
