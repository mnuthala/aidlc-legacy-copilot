---
name: ant-build-test
description: "Execute verified Ant builds and JUnit4 test suites."
---
# Procedure

Discover actual Ant targets and dependency repositories; do not assume Maven/Gradle. Confirm Java 8 compilation and separate harness Python runtime. Configure argv adapters only after running known commands manually. Every suite emits fresh JUnit XML beneath AIDLC_RUN_DIR/reports. Reject nonzero exits, zero tests, skipped cases and missing reports. Preserve EasyMock/Selenium/Cactus working conventions.

# Contract

Read docs/STACK.md and the selected change inputs. Preserve source/requirement references. Persist outputs to changes/CHANGE-ID. Use templates where relevant. Do not modify controls or self-approve. Report blockers with the decision needed and affected artifacts.
