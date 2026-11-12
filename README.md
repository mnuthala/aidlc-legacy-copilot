# AIDLC harness for a Java 8 legacy monolith
A supervised GitHub Copilot starter for requirements -> stories/quality -> HLD/LLD -> tasks/test plan -> human approval -> implementation/tests -> execution -> bounded repairs -> independent review -> human release review.

Includes 14 Copilot agent profiles, 18 skills, source/path instructions, design/backlog templates, a standard-library Python controller, cryptographically signed human approval receipts, adapter contracts and automated controller tests.

Start with [Operating guide](docs/OPERATING_GUIDE.md), [Architecture](docs/ARCHITECTURE.md), [Stack](docs/STACK.md), and [Quality rubric](docs/QUALITY_RUBRIC.md).

```
python3 -m unittest discover -s tests -v
python3 harness/aidlc.py --help
```

No Python packages are required; no PyYAML dependency. OpenSSL is required for approval verification. Copilot agents perform content generation once installed in your application repository and invoked with your BRS/design context. No BRS, codebase, Ant targets or test environment was supplied; adapters intentionally remain disabled and all document templates are drafts.

Trust and enforcement: signed approvals bind exact reviewed artifacts, but local Python code and writable files are not a sandbox. Run authoritative checks with protected controller code/trust/evidence outside worker control before unattended enterprise use. Human merge and UrbanCode release approval remain external.
