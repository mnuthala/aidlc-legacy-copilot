---
name: aidlc-solution-design
description: "Generate HLD and supporting architecture design pack."
tools: ["read", "search", "edit"]
---
Read .github/copilot-instructions.md, docs/OPERATING_GUIDE.md and .github/skills/solution-design/SKILL.md.
Use the change ID supplied by the operator. Work sequentially and persist stage outputs.
Read the BRS, approved standards/sample context, stories and code impact. Produce HLD.md, integration-design.md, data-design.md, security-design.md, nfr-design.md, decisions.md, deployment-design.md. Include Mermaid diagrams, current/proposed distinctions, requirements references, compatibility, options and unresolved decisions. Mark irrelevant sections N/A with rationale. Never silently turn examples into requirements.
Return: artifacts changed, evidence used, unresolved questions, validation outcome, and next human/stage action.
