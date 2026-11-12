---
name: detailed-design
description: "Translate HLD into an implementable legacy application LLD."
---
# Procedure

Use LLD.md template. Specify existing/proposed symbols, method contracts, processing and error paths, Struts/custom MVC/JSP/configuration impacts, SQL/mappings, contracts, transactions/cache, scripts and tests. Explicitly identify generated files and regeneration commands. Tie every change to story/AC and HLD sections. Unknown commands remain blockers.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
