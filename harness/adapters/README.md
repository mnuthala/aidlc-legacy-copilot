# Configure application adapters
No application adapter is enabled by default. Set `harness/config.json` argv arrays only after verifying your existing Ant targets and approved environment.
Example shape (illustrative target name; discover yours): `["ant", "-f", "build.xml", "your-unit-target"]`.
The process receives AIDLC_CHANGE, AIDLC_SUITE and the unique absolute AIDLC_RUN_DIR.
Your Ant target/wrapper MUST write or copy fresh JUnit XML into `$AIDLC_RUN_DIR/reports/` before returning. Configure report_glob relative to AIDLC_RUN_DIR. Never copy an old report directory without ensuring the tests just ran; the wrapper is responsible for test freshness and correct deployed candidate provenance.
The controller records exit status and rejects zero tests, skipped cases, XML failures and missing reports. It rejects source mutation during execution. Build outputs must live outside source_roots.
Never put credentials in argv/config/logs. Use a controlled test credential broker/environment. Test deployment is deliberately not automated by this starter; attach approved UrbanCode provenance to deployment-design.md and runtime evidence.
