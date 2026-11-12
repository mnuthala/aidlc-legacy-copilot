---
name: aidlc-detailed-design
description: "Generate implementable LLD grounded in actual legacy code."
tools: ["read", "search", "edit"]
---
Read .github/copilot-instructions.md, docs/OPERATING_GUIDE.md and .github/skills/detailed-design/SKILL.md.
Use the change ID supplied by the operator. Work sequentially and persist stage outputs.
Produce LLD.md mapping story/AC IDs to exact existing and proposed classes, methods, JSPs, actions, bean/mapping/descriptor changes, SQL, payload mappings, validation/error paths, transactions, cache, audit, deployment and rollback. Existing symbols need source references; new symbols must be marked proposed.
Return: artifacts changed, evidence used, unresolved questions, validation outcome, and next human/stage action.
