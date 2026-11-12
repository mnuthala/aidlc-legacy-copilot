---
name: test-planning
description: "Design layered tests from acceptance criteria."
---
# Procedure

Use test-plan.md and test-cases.json. Cover unit/functional/integration/regression and existing-behaviour characterisation. Include boundary/negative/permissions and transaction outcomes as applicable. Provide fixture setup/cleanup, expected outcomes and exact automation IDs matching emitted JUnit XML. Explicitly distinguish stubbed tests from real WAS/Oracle/MQ/SOAP integration.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
