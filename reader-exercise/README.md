# Offline reader exercise UI

Software preparation only. No recruitment, actual sessions, authenticated identity,
human observations or measured benefit. Every automated test uses `?test=1`, displays
**SYNTHETIC SOFTWARE TEST**, and exports `synthetic_test: true`. Ordinary mode exports
false; a code or client timestamp does not prove a human participant exists.

The generator copies **only** `index.html`, `app.js`, and `style.css` into its new
served root before sealing. Serve that generated root on loopback, never this
repository or the private root. The UI needs local HTTP (fetch is unavailable under
`file://`), but has no external dependencies, fonts, network services or inference.

```sh
python3 -m http.server 5181 --bind 127.0.0.1 --directory /path/to/generated/served
# Browser: http://127.0.0.1:5181/?test=1 for software validation only.
```

The UI reads `manifest.json`, `export-contract.json`, common `Q01-B.json` practice,
and only the assigned `F01`–`F04` A/B assets. Familiar demo positions 1, 2 and 7
are excluded by the generator. The operator must still check actual participant
unfamiliarity. Views are labeled A/B; hypotheses, annotations, reference metrics,
field filenames and condition decoding are not displayed or fetched. This is
hypothesis/reference blinding, not complete participant blinding or access control
for public data. B exposes real run 1–8 outlines and component disagreements; A
uses baseline outlines only. No mask edits or automatic tally answers occur.

Consent requires an assigned P01–P06 code, explicit retention choice and operator
readiness acknowledgement. Common practice uses tiles 0–3 of Q01 in view B for
every allocation; practice must be completed before assessment and is not exported.
All field and PNG assets decode before Start is enabled. The viewer and entries
remain hidden until Start. Actual elapsed milliseconds use `performance.now()`;
UTC timestamps use the client clock. Visibility transitions record monotonic offsets
without pausing timing. No visible-time duration or authentication claim is made.

Every started assessment has its four assigned region records. Confirmed regions
require whole tallies 0–1000 and uncertainty 0–3. Unresolved regions need a reason;
their task finishes as `failed`, since the contract has no task-level unresolved
status. Other incomplete/failed/aborted tasks require reasons. Partial entries have
region status `not_started` until confirmed or marked unresolved, per the contract.
An export during an active assessment creates an `aborted` snapshot with an explicit
incomplete-at-export reason and observed export time; the task continues in memory.
Unstarted tasks are omitted (missing), not assigned invented times. A pre-start
asset failure remains unstarted and offers retry rather than fabricating a record.

All data stays in memory until an explicit local JSON download. Reload/close loses
it; downloads remain on disk. No automatic uploads, localStorage or IndexedDB.
Free text warns against names/contact details; it cannot guarantee de-identification.
Withdrawal clears in-memory task data and exports a request with `retention_choice:
"delete"` and `tasks: []`. It does **not** delete existing downloads or operator
copies. The operator must handle the request; the scorer rejects withdrawn records.
Never commit or publish raw exports. Default scoring rejects synthetic exports;
`--allow-synthetic` is software validation only.

Assignment hashes and field/configuration metadata are checked. If a public
manifest exposes raw file SHA-256 values in `asset_sha256`, `asset_hashes`,
`served_files`, or `seal.served_files` (filename → hex digest or `{sha256}`), each
supplied hash is checked before use. Absent public seal hashes are explicitly
reported; no unavailable seal, signature or authenticity is invented. The private
seal is never fetched. Unexpected asset keys fail closed.

## Synthetic browser checks

Use existing Playwright dependencies, without global installs:

```sh
NUCLEILENS_READER_URL=http://127.0.0.1:5181 node reader-exercise/tests-reader-browser.mjs
```

The test resolves Playwright from this repository’s `frontend/package.json`
without changing dependencies. Set `NUCLEILENS_READER_DEPS_PACKAGE` to another
existing frontend `package.json` if needed. Tests refuse non-loopback URLs and add
`?test=1` themselves. They read actual
generated assets, inspect real image/alternative layers, exercise all four task
outcomes and partial export/withdrawal, assert the contract and timing bounds, test
synthetic visibility-event handling (not physical tab-background behavior), keyboard reachability, mobile layout and loading/hash errors.
Fault tests alter responses in browser memory only; generated files stay untouched.
Tests keep downloaded synthetic JSON in memory by default and print a software-check
summary. For browser-to-scorer integration, explicitly set
`NUCLEILENS_READER_SYNTHETIC_EXPORT` to a new file under `/tmp/`; it stays labeled
synthetic and must never be committed or presented as human observations. Run only against the owned
generated local bundle.

The first headless visibility check failed: freezing the browser lifecycle did
not produce visibilitychange. The corrected software check dispatches an explicitly
synthetic event and records actual monotonic offsets. It does not prove real
physical-tab interruption handling. Both results are retained in evaluation/checks.
