# Independent release and browser review

Reviewed on 2026-10-12 against the frozen working sources recorded in [source-map.json](source-map.json), following base commit `96945549ab0466c26300a2863f907cf20da35042`. This review covers the new release/browser delta, not the older implementation map. It is not a fresh aggregate-gate result, merge approval, AWS deployment, hosted launch or store publication.

The delta contains four capability documents, 26 requirement operations (24 ADDED and 2 MODIFIED) and 57 scenarios. Its cloud modifications follow `cloud-deployment-customer-access`; pending specifications must be archived in that dependency order. Written scenarios are not claims that every live acceptance scenario ran.

## Disposition

No unresolved concrete implementation blocker remains in the reviewed deployment, prepared preview, store helper or encrypted operator handoff scope. The positive software includes separate QA/prod orchestration, conflict-safe CNAME registration, exact public web verification, isolated fictional preview, real-device store build/inspection/submission/status and protected read-only reconciliation. Genuine release inputs and acceptance remain required.

Initial submission is supplied by the Python helper with persistent protected operator storage. The optional Actions workflow supports plan, build, reconcile and status; it refuses fresh uploads because an ephemeral runner cannot retain the sole upload fence after runner loss. Packing original signed operator evidence provides a usable encrypted transfer for reconciliation without repeating the upload.

## Findings corrected and re-reviewed

| Finding | Reviewed correction and meaningful evidence |
|---|---|
| DNS lookup followed by UPSERT could overwrite a concurrent foreign record | Atomic absent-record CREATE, exact-equivalent no-op, conflict refusal and no invented change ID. |
| Minimal distribution checks could accept a disabled or foreign release route | Actual enabled/deployed single regional S3 origin, exact release prefix, empty OAI, SigV4 always-signing OAC; unexpected origins, cache behaviors and origin groups refuse. |
| Authority/evidence reads could follow links, block on special files or allocate before a bound | Stable nonblocking/no-follow regular-file snapshots; private ownership/link/mode controls; actual FIFO, symlink, oversized and replacement regressions. |
| ZIP digest and contents could come from different reads | One bounded snapshot supplies both archive digest and member validation. |
| CSP substring checks and unbounded public responses overstated verification | Complete exact index/deep-link policy, required headers and bounded identity-encoded byte/digest verification; weakened policy, overrun and compression refuse. |
| DNS waiter could report late success beyond ten minutes | Original monotonic successful-observation budget and post-response refusal; SDK socket/retry delay in reporting failure is documented without cancellation or rollback claims. |
| Preview could mix ordinary exports/account origins or reuse an unrelated service | Separate fixed-origin guest export, no dotenv, cleared Metro, source/export receipt checks, exact manifest/index readiness and preservation of unrelated processes. |
| Default preview fetch followed redirects | Explicit redirect refusal; actual controlled redirect target receives zero requests. |
| Verifying an EAS archive did not bind a later unchecked CLI fetch | Locked isolated installation, verified official SHA-512 archive, installed CLI source comparison and execution of that inspected local entrypoint. |
| Generic jarsigner success could accept appended unsigned payload | Strict actual JAR verification against the independently selected upload certificate; an actual signed JAR with an unsigned appended entry is rejected. |
| Project/build metadata alone could misidentify a candidate | Authenticated exact project preflight, actual package/version/minimum SDK and embedded runtime/signature inspection, current source/backend/callback admission and exact provider UUID. |
| Local CLI children or late completion could outlive bounded execution | Owned process-group cleanup on normal parent exit and failure, post-completion original deadline/output checks; actual child-process and controlled late-completion regressions. |
| A closed file did not establish durable pre-upload intent storage | Exclusive 0600 signed intent, file flush/fsync and directory fsync/identity barrier before upload; actual descriptor-order tests and both barrier-failure cases refuse provider calls while preserving the fence. |
| Ephemeral Actions intent publication after upload could permit duplicates following runner loss | Fresh automated upload is refused before private staging/provider action. Exact original signed intent and provider UUID are mandatory for reconciliation and checked again before executing the helper. |
| Restricted reconciliation lacked a practical original-intent transfer | Mutation-free pack validates original signatures/scope/byte links, AES-GCM seals exact signed wire bytes, enforces the 48-KiB secret cap and supports a mutually exclusive protected ciphertext or same-repository artifact input. |

## Verification performed

Independent focused executions completed with no failures or skips:

| Execution | Passed | Actual boundary exercised |
|---|---:|---|
| Release/provenance/web deployment tests | 43 | Stable file/body reads, DNS conflict/deadline and policy/admission behavior; AWS boundaries remain doubles. |
| Codespaces preview tests | 6 | Disposable Git repositories and real loopback HTTP/process behavior; no hosted account/session. |
| Store helper tests | 33 | Actual JDK signatures, owned processes and storage barriers; provider/macOS signing boundaries remain doubles. |
| Protected store input/handoff tests | 50 | Actual cryptography, private file handling and pack-to-reconciliation preservation; GitHub/provider boundaries remain doubles. |

The owners additionally recorded actual guest-browser journeys and lifecycle probes. The final combined helper run recorded 83 tests plus 208 subcases, with 85.0556% store-helper and 95.9259% materializer statement coverage and zero exclusions. Those focused results do not replace the complete mandatory repository gates or authenticate a real store candidate. Source hashes and evidence boundaries are recorded separately in the ledger.

The `9694554` checkpoint passed seven local categories and thirteen GitHub jobs. Its tested PR merge was `ae530e6e8642b640782f0c0cc8f0a25b48a69c0d`, independently equivalent at Git tree `1482001b2ab43d8edeb75a4b68dfb488db135c4a`. It does not verify this changed source. Effective-main rules and existing rulesets were empty; Administration returned 403. Workflow success does not enforce merges.

## Remaining implementation and authentic external boundaries

- A portable selective saliva driver still needs a selected assay's complete vendor protocol, controls and analytical calibration. The implemented no-BLE collection and independent reference-lab import are positive software, not a quantitative portable assay.
- A complete breath sampling/calibrated instrument driver still needs an actual selected interface. A bare fuel-cell or generic ADC does not define sampling flow or valid mg/L conversion.
- Human ECG remains unavailable without an independently observed power/charging/cable/isolation interface and whole-system safety evidence. Participant declarations do not measure those states; simulator/bench acquisition is separate.
- Actual study/operator assignment, assay/device/optical/electrical/timing qualification, independent datasets and prospective model validation remain unseeded. Current conditional research and HR authority software do not create those approvals or a driving-clearance claim.
- Intended AWS accounts/domains/certificates/release authority, independent QA acceptance, actual QA/prod rollout and authenticated customer probes remain unexecuted. Appetize/Codespaces account launches, genuine Apple/Google/Expo credentials/signing/processing/review and tester/public availability are not established by this review.
- All seven local categories and thirteen GitHub jobs must pass again for final frozen source with strictly greater than 80% unit inventories and no mandatory skips. Actual required merge enforcement, including administrators, remains a separate prerequisite. This review does not close those tasks.

The [release and browser guide](../../../../docs/RELEASE_AND_BROWSER_TESTING.md) documents actual commands, input custody, partial failure, persistent initial store submission, encrypted transfer and customer installation boundaries. The [task checklist](../tasks.md) preserves outstanding global and external acceptance.
