---
name: was9-integration-testing
description: "Execute container-dependent tests against approved WAS9."
---
# Procedure

Require a representative nonproduction deployment through authorised UrbanCode process. Confirm deployed candidate digest/package provenance, fix pack, class loading, JNDI, EJB2, Servlet levels, datasource, SOAP and MQ bindings. Run real integration suites and record environment evidence. Mocked tests cannot establish container correctness. Never claim production readiness solely from compilation.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
