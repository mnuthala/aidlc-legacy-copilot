---
name: aidlc-task-planning
description: "Generate sequenced implementation and verification tasks."
tools: ["read", "search", "edit"]
---
Read .github/copilot-instructions.md, docs/OPERATING_GUIDE.md and .github/skills/task-planning/SKILL.md.
Use the change ID supplied by the operator. Work sequentially and persist stage outputs.
Populate tasks.json. Cover source/configuration/database/deployment/test/evidence work. Every task needs story_ids, design_refs, depends_on, deliverable, done_when and verification. Provide sizing assumptions in test-plan.md or review-record.md; do not invent precise estimates. Ensure dependency graph is acyclic.
Return: artifacts changed, evidence used, unresolved questions, validation outcome, and next human/stage action.
