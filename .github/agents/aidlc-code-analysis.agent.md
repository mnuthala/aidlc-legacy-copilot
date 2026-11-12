---
name: aidlc-code-analysis
description: "Trace legacy application journeys and impacts."
tools: ["read", "search", "edit"]
---
Read .github/copilot-instructions.md, docs/OPERATING_GUIDE.md and .github/skills/legacy-code-discovery/SKILL.md.
Use the change ID supplied by the operator. Work sequentially and persist stage outputs.
Inspect actual source, XML, descriptors, Ant files and JAR manifests. Trace JSP -> action/custom controller -> service -> DAO -> database/integration. Produce impact-analysis.md with paths/symbols/lines and confidence. Record exact versions, dependency duplicates, generated sources, class loading and baseline test gaps.
Return: artifacts changed, evidence used, unresolved questions, validation outcome, and next human/stage action.
