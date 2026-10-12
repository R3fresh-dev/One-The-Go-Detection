# Independent fixture clock follow-up

Reviewed on 2026-10-12 after main Actions run `38209009044` failed the API unit and PostgreSQL jobs on the same consent test. The prior `a6606b1a41be7144684927851a0566679e5e6598` local seven-category result and PR run `38208566261` remain historical; they do not replace fresh checks for this follow-up. This document supplements the original 52-source audit without rewriting its snapshot or evidence.

## Cause and correction

The old consent decorator evaluated `iso(now()+60)` during module collection. A slow prefix could consume those sixty seconds before the request, making the acknowledgment a legitimate past value. The observed 201 response then contradicted a stale fixture's expected 422; production correctly permits queued past acknowledgment under current consent authority.

[test_consent_versions.py](../../../../services/api/tests/test_consent_versions.py) now parametrizes case labels and constructs the future timestamp after setup, immediately before POST. The negative/unconfirmed cases, exact 422 assertion and absence of a consent receipt remain unchanged.

A related collection-time risk was found proactively in [test_identity_barriers.py](../../../../services/api/tests/test_identity_barriers.py): separate `int(now())+1` and `int(now())` calls could cross a second boundary and become equal, silently losing the intended invalid ordering. It now constructs labeled cases at request time from one captured integer timestamp. Future floating expiry remains a nonexpired float, so the 401 case still tests strict typing. Boolean/negative claims and exact 401 expectations remain unchanged.

## Independent controlled proof

The reviewer used isolated SQLite and temporary, uncommitted experiment files. Only collection and fixture clock references were simulated; the API's request-admission clock references stayed real, and production source was unchanged. The consent experiment presented collection as one hour earlier, then restored the real clock before requests. The identity experiment supplied fixture clock reads across a second boundary and asserted that each corrected case captures only one timestamp.

| Experiment | Actual outcome |
|---|---|
| Preserved old consent test under delayed collection | Its future case became past: 201 instead of expected 422; the other two cases passed. |
| Corrected consent cases and legitimate queued-past acceptance under the same delay | 4 passed, zero skipped. Future/negative/unconfirmed still reject; legitimate past acknowledgment still accepts. |
| Preserved old JWT test under controlled rollover | Its ordering case became equal: 200 instead of expected 401; the other four cases passed. |
| Corrected JWT cases under controlled rollover | 5 passed, zero skipped; one captured clock per case, strict 401 retained. |
| Corrected consent cases under ordinary execution | 4 passed, zero skipped. |

The two reproduced failures are explicitly observations of preserved old fixture blocks, not waived failures, xfails or skipped checks in the current suite. Other cases, including PostgreSQL serialization, were outside these focused reviewer executions. The backend owner additionally reported both full fixture modules passing 23 SQLite cases with one PostgreSQL case deselected; the mandatory live gate must still execute that case.

Temporary experiment scripts, JUnit reports and the detailed follow-up record are retained under `/tmp/otgd-consent-collection-clock-review`. They contain fictional fixture evidence and are not cloud/store/scientific acceptance.

## Frozen source boundaries

| File | SHA-256 |
|---|---|
| services/api/tests/test_consent_versions.py | `6e8bad49a768eadede3872785faf6c95ee2c423d7b61bd9e225090124d021f78` |
| services/api/tests/test_identity_barriers.py | `771273aca97670274d16cf11118be13381a278d43433bc975bc82446d8bc9ca0` |
| services/api/otgd/main.py, unchanged from a6606b1 | `172463ca953ae1bf555a4258010f1511ed8af3b61359a9d8ab08bf9a2e6f7fdc` |
| services/api/otgd/auth.py, unchanged from a6606b1 | `865f4d0fcf199b9898d3bb43fd5301f814979d47f01ea48d9be2df75063c4fd7` |

The reviewer independently compared the two production files byte-for-byte with the base. Consent still rejects timestamps beyond the five-second future allowance or before the epoch. Authentication still requires integer time claims and `auth_time <= iat < exp`; no runtime authority, threshold, signing verification or privacy rule changed. The parent separately verified unchanged production runtime inputs before retaining the existing local services.

No unresolved blocker remains in this narrow fixture correction. All seven local categories and thirteen required GitHub jobs must pass again for final committed source without mandatory skips or lowered thresholds. This review does not approve a merge, establish actual branch enforcement or declare those pending gates complete.
