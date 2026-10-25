# Hosted preview unit identity isolation — preflight

Run `otgd-20261025-0555`; D009v10; correction **1/2**, recovery **0/3**. Checkpoint9 `52ffa1044e787f7fea088c82797d4525af02e9a3` CI preview failures remain historical failures. This report records a narrow test fixture repair, not final candidate or release signoff.

## Reproduced cause and repair

Read the actual hosted-native-preview workflow, unit coverage runner, runtime adapter, Constants adapter and production BUILD admission before editing. Both preview jobs inherit the workflow's disabled `unavailable.invalid` public identity. The unit Constants adapter already supplied the fictional localhost issuer, client and native callback, but omitted the newly compiled hosted OAuth origin and web callback. BUILD therefore inherited those two disabled artifact values from the job environment. The production endpoint guard correctly refused the inconsistent fixture metadata with `AUTH_ENDPOINT_INVALID`.

Reproducing `auth.test.ts` plus `hosted-preview.test.ts` with all 11 actual top-level workflow environment entries produced **19 failures / 8 passes**, exit1, with that exact error. Raw evidence: `/tmp/otgd-preview-unit-red.log`. No production permissiveness was needed.

The sole fixture repair adds explicit `oauthOrigin: http://localhost:8081` and `webCallbackUri: http://localhost:8082/` to `tests/support/constants.cjs`. Production config/auth admission, SDK state/PKCE behavior, coverage runner, source inventory, strict >80 threshold and workflow/artifact pins are unchanged.

New `tests/unit-build-isolation.test.ts` reads the actual workflow environment and launches isolated Node unit processes for both ordinary and guest fixtures. It asserts the complete consistent fictional build identity while the ambient disabled OAuth pins remain intact. A separate child loads actual `app.config.ts` without the test adapter and requires the original disabled guest artifact pins. Before the fixture repair, the two adapter cases failed with `unavailable.invalid` instead of localhost; the artifact case passed. Raw RED: `/tmp/otgd-preview-isolation-regression-red.log`.

## Actual verification

- Focused auth, Cognito, callback/401 acceptance, hosted guest, OAuth build and new isolation cases: **34 passed, zero failures/skips**; `/tmp/otgd-preview-isolation-focused.log`.
- Exact hosted workflow environment: `npm run typecheck` and `npm run test:coverage` both exit0. **373 passed**, zero failed/cancelled/skipped/todo; coverage **18472/20340 = 90.81612586037365%**. `/tmp/otgd-preview-coverage-green.log`, machine `/tmp/otgd-preview-coverage-green.json`, raw events `/tmp/otgd-preview-coverage-events.log`.
- Ordinary environment, with APP_ENV/EXPO_PUBLIC_* and unit-mode build overrides absent: full `npm run test:coverage` exit0, the same **373 passed**, zero failed/cancelled/skipped/todo and **90.81612586037365%**. `/tmp/otgd-ordinary-coverage-green.log`, machine `/tmp/otgd-ordinary-coverage-green.json`, raw events `/tmp/otgd-ordinary-coverage-events.log`.
- Both machine reports bind source inventory SHA256 `4dd18f87f2267c5e017e00cede67a306064a926e3fa0a5fe94094e304c8085e8`. Unloaded `src/platform/sharing.native.ts` remains counted as zero. Existing guest no-network, hostile build environment and endpoint refusal assertions all executed; no test filtering, skipping or threshold adjustment.
- Prettier and `git diff --check` exit0. An initial new-test typecheck failure from React Native's global URL type versus Node's URL type was corrected by importing `URL` from `node:url`; both failed attempts remain in `/tmp/otgd-preview-isolation-typecheck.log` and `/tmp/otgd-preview-coverage-attempt1-typecheck.log`. The successful exact-environment log records the later typecheck exit0.

The reproduction environment was extracted from the actual workflow's top-level `env` block, preserved in `/tmp/otgd-preview-coverage-env.json`, and overlaid only in subprocesses. These commands did not change the shell's artifact environment or any deployed service.

## Source binding and remaining limits

`/tmp/otgd-preview-isolation-source-hashes.json` binds the two changed/new test files, ten unchanged direct config/runner/artifact sources and all twelve external evidence files. Constants SHA256 `c0a09a0900163da61f06c53ac9bc44274786c54380d794c359792ebe850b094b`; new test SHA256 `829a6ca78ac16082018846bc916ddb3674c85bde8a5ee7db54951305e9d2c6cf`.

No production, workflow, coverage runner, dependency installation, Docker, browser port, retained data or native artifact build action occurred. Actual Android/iOS preview compilation and the final current CI rerun remain pending; these local unit/config results do not replace them. All owned test/report writes and the shared coverage output slot are released.
