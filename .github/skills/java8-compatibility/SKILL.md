---
name: java8-compatibility
description: "Implement compatible Java 8 changes in the existing monolith."
---
# Procedure

Confirm actual compiler source/target and installed library APIs. Keep traditional javax/container conventions; do not introduce modern Spring/Jakarta or upgrade dependencies without approval. Follow nearby proven patterns. Preserve exception, resource, encoding and transaction behaviour. Inspect packaging to avoid duplicate classpath changes.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
