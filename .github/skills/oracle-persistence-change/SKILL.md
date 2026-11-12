---
name: oracle-persistence-change
description: "Implement Oracle/Hibernate/iBATIS changes safely."
---
# Procedure

Discover per-module Hibernate 2/3 and iBATIS APIs, Oracle version, ojdbc JAR and JNDI/DBCP ownership. Check SQL bindings, precision/null/date semantics, lazy loading, transaction rollback and EhCache invalidation. Use approved test schema. Supply migration prechecks/verification/recovery; do not silently use an in-memory DB as Oracle integration evidence.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
