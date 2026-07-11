# HyperAgent Platform Facts

## Observed
- HyperAgent is Airtable’s hosted AI agent platform for always-on, workflow-oriented agents.
- Public HyperAgent skills are published as individual JSON files and loaded at runtime.
- Airtable describes HyperAgent as an agent execution platform tied to structured operational data, connected tools, and governance/human oversight.
- Public examples center on repeatable business workflows: design systems, content production, ops, and data-viz.

## Inferred
- A skill should describe reusable work, not one-off prompts.
- A deployed role should declare triggers, tools, budget boundaries, and evaluation criteria.
- A fleet needs explicit handoff conventions if multiple agents share a workflow.
- Credentials should live in env vars or a secure store, not in the skill payload.

## Speculative
- Exact auth endpoints and deployment APIs may differ by account tier or product version.
- Browser, shell, code execution, and integrations are likely exposed as platform tool grants, but the precise configuration shape must be verified in live docs.
- Skill import/export may support JSON-first payloads with platform metadata layered on top.

## Source Pointers
- Airtable article on agent skills: https://www.airtable.com/articles/ai-agent-skills
- Airtable article on agent frameworks: https://www.airtable.com/articles/ai-agent-framework
- Airtable article on AI agents: https://www.airtable.com/platform/ai-agents
- Public examples: https://github.com/alexmcdonnell-airtable/hyperagent-public-skills
- Secondary note with inventory of example skills: https://notes.nicolasdeville.com/github/hyperagent-skills
