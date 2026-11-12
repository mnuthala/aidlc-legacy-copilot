---
name: legacy-document-testing
description: "Validate JasperReports, POI, Velocity and iText output."
---
# Procedure

Inspect exact per-module versions, template paths, fonts and encoding. Check report compilation APIs and generated output. Assert spreadsheet cells/types, document text/totals and required visual layout. Normalise only known nondeterministic fields. Keep representative golden samples reviewed by humans.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
