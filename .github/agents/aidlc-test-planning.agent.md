---
name: aidlc-test-planning
description: "Plan unit, functional, integration and regression tests."
tools: ["read", "search", "edit"]
---
Read .github/copilot-instructions.md, docs/OPERATING_GUIDE.md and .github/skills/test-planning/SKILL.md.
Use the change ID supplied by the operator. Work sequentially and persist stage outputs.
Produce test-plan.md and test-cases.json covering every acceptance criterion. Specify data, environment, scenario, expected results, suite and exact future JUnit XML classname#name automation ID. Distinguish mocks from real integration tests, baseline failures and blocked tests. Include security, boundary, negative and rollback cases as relevant.
Return: artifacts changed, evidence used, unresolved questions, validation outcome, and next human/stage action.
