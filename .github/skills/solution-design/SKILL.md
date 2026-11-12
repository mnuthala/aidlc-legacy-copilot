---
name: solution-design
description: "Generate HLD and supporting architecture documents."
---
# Procedure

Use harness/templates/*-design.md and HLD.md. Separate sample document style from mandated architecture standards; conflicts go to a human. Define current/proposed components, major flows, data, security, nonfunctional behaviour, compatibility, deployment and tradeoffs. Mermaid must remain readable. Map each element to requirements/story IDs. Use N/A with explanation for unaffected areas; never invent missing source facts.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
