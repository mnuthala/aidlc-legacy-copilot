# Operating guide
## 1. Install into the application repository
Merge this starter's .github/, harness/, docs/ and tests/ folders carefully on a feature branch; do not overwrite existing instructions/workflows. Python 3.10+, OpenSSL, GitHub Copilot access and optionally the current Copilot CLI are required. Keep the harness runtime separate from Java8.
Set repository_id and source_roots in harness/config.json to ALL application inputs affecting packaging and tests: Java, JSP, XML, SQL, resources, build files, tests and locked dependency manifests/JARs as applicable. Build/report/cache output folders must not be inside those roots. Missing roots fail closed. Commands execute at repository root.
Configure each adapter argv with verified commands. Default null adapters intentionally block execution. No real application was supplied to create/verify these commands. Use harness/adapters/README.md.

## 2. Initialise a change
Convert BRS and sample context to reviewed UTF-8 Markdown/text if practical. Original binary documents may be copied but require a capable document extraction tool before an agent can interpret them.
```
python3 harness/aidlc.py init CHANGE-123 --brs /path/to/brs.md --context /path/to/sample-design.md
```
This copies the inputs and draft templates, and records a source baseline. Template TODO markers must be replaced through evidence-backed analysis. There are no fabricated completed designs.

## 3. Run planning agents
In Copilot Chat select profiles in this order: aidlc-requirements, aidlc-code-analysis, aidlc-story-quality, aidlc-solution-design, aidlc-detailed-design, aidlc-task-planning, aidlc-test-planning, aidlc-design-review. Give each the change path.
Alternatively obtain a prompt with `python3 harness/aidlc.py prompt CHANGE-123 --agent aidlc-requirements` or launch `python3 harness/aidlc.py invoke CHANGE-123 --agent aidlc-requirements` with Copilot CLI installed. This uses --agent/--prompt and preserves normal tool permissions. There is no blanket auto-approval and no automatic agent fan-out.
Planning agents must edit change documents only; inspect actual code read-only. Refine until questions are resolved. Use `python3 harness/aidlc.py validate CHANGE-123` to check required fields, score thresholds, document completeness, task cycles and requirement/AC/test links.

## 4. Human approval
Copy harness/trust-store.example.json OUTSIDE the repository to a controller-owned directory. Set repository_id and reviewer roles. Each reviewer creates a private key on their own machine (never the worker), e.g. `openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out reviewer.key`, then `openssl pkey -in reviewer.key -pubout -out reviewer.pub`. Restrict private key permissions. Copy ONLY public keys to the protected trust directory. Update public_key paths relative to trust JSON.
Set AIDLC_TRUST_STORE to the absolute trust JSON path on the authoritative controller host. Agent workers must not have write access to trust files or access to private keys. Local use without OS separation is advisory only.
```
python3 harness/aidlc.py approval-request CHANGE-123 --gate plan
```
Reviewers inspect the actual pack and verify the payload digest using the protected controller; do not approve a digest solely because a worker sent it. Transfer the request JSON to each reviewer workstation and run the reviewed signing helper:
```
python3 sign_approval.py approval-request-plan.json --reviewer alice --private-key /private/alice.key --out alice.json
```
Return receipts to changes/CHANGE-123/approvals/plan/alice.json (one per reviewer). All required roles must be satisfied; roles are assigned only by the trust store. Recheck `python3 harness/aidlc.py authorize CHANGE-123 --gate plan`. Editing plan/inputs/control files invalidates approval. Do not edit the baseline to avoid a stale approval.

## 5. Implement and execute
Invoke aidlc-implementation then aidlc-test-implementation only after plan authorisation. Runtime edit access is a host policy: prompt rules cannot prevent a user from editing files directly.
Run all stages sequentially:
```
python3 harness/aidlc.py run CHANGE-123 --suite build
python3 harness/aidlc.py run CHANGE-123 --suite unit
python3 harness/aidlc.py run CHANGE-123 --suite functional
python3 harness/aidlc.py run CHANGE-123 --suite integration
python3 harness/aidlc.py run CHANGE-123 --suite regression
```
Capture a pre-change baseline with `baseline CHANGE-123 --suite unit` etc. Baseline runs never count as candidate passes. Record known failures and ensure planned/new tests are independently meaningful.
Adapters must verify deployed candidate provenance for remote functional/integration tests. The controller cannot infer which WAR is deployed from a successful remote response. Keep such evidence beside the run, include it in human review, and add a trusted environment attestation adapter for unattended use.
A planned test automation_id must match XML classname#name in its assigned suite. Source changes invalidate old passes; all required suites need current evidence. Missing/skipped/zero tests never pass.

## 6. Repair and review
Classify failures first. Record each permitted repair before editing:
```
python3 harness/aidlc.py repair CHANGE-123 --failure FAIL-001 --diagnosis "Reproduced approved rule violation in controller validation"
```
Stop after per-failure or overall budget. Environment failures and ambiguous requirements require humans. Fix agents cannot change approved criteria, disable assertions or widen permissions. Human must approve material plan changes.
Invoke aidlc-review to create implementation-review.md, then `python3 harness/aidlc.py evidence CHANGE-123`. Evidence succeeds only with current build/tests, observed planned cases and an implementation review. Request/sign release approval using the same workflow with --gate release and approvals/release/. Finally run `authorize CHANGE-123 --gate release` on the protected host. Release means reviewed candidate readiness; merging/promotion stays a separate human-controlled process.

## Limits and deployment checklist
The CLI is a supervised starter, not an installed enterprise orchestration service. Local state is recomputed from artifacts; operations must be sequential. Local writable run results/counters can be tampered with by the same OS user. Protect execution/evidence storage and run pinned controller code outside the worker for enforced operation. There is no webhook daemon, GitHub identity resolution, issue creation, production credentials, durable audit server or automated deployment.
Story scoring and document checks validate structure, not correctness. Configure source roots carefully and review all omitted assets. External dependencies and test environments were not available for this package's validation.
