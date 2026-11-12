---
name: failure-diagnosis
description: "Diagnose failures and perform bounded repairs."
---
# Procedure

Read the failing run and compare baseline. Classify application defect/test defect/environment/baseline/ambiguity. Preserve the approved acceptance oracle; register each repair attempt using stable failure ID before mutation. Fix smallest cause, rerun target then required suites. Stop after three attempts per failure or total budget, and escalate scope/security/contract changes.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
