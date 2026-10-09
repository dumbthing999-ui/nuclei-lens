# Deployment and local recovery

Production: https://nuclei-lens.dumbthing999.chatgpt.site
Public source: https://github.com/dumbthing999-ui/nuclei-lens

## Recover immediately on the judge's machine

The precomputed real examples need no runtime startup. If the origin is down,
use the checked source and pinned installation commands in README. Prepare the
runtime once while online, then build and serve the entire static directory:

```bash
npm ci --prefix frontend
node scripts/sync_engine.mjs
node scripts/prepare_runtime.mjs
.venv/bin/python scripts/collect_notices.py
npm run build --prefix frontend
node scripts/copy_site_dist.mjs
python3 -m http.server 8080 --bind 127.0.0.1 --directory frontend/dist
```

Open http://127.0.0.1:8080. Static images, shared scientific code and runtime
libraries are self-hosted. Live inference still runs in the browser. No API keys
are needed. After assets are present, serving the complete build works locally
without an external inference API; this is not a service-worker/offline-cache
promise for a previously visited production page.

## Preserve a release build

The release operator retains an ignored static deployment archive under
`artifacts/nucleilens-site-v6.tar.gz`, with `.openai/hosting.json` and complete `dist/`.
The package check requires loader/WASM/stdlib/lock files and verifies all runtime
and wheel hashes plus exact built/source Python engine bytes. Generated runtime
assets are ignored by Git; a successful Vite build alone is insufficient.
Verify the retained checksum before extracting:

```bash
sha256sum -c artifacts/nucleilens-site-v6.tar.gz.sha256
mkdir /tmp/nucleilens-restored
tar -xzf artifacts/nucleilens-site-v6.tar.gz -C /tmp/nucleilens-restored
python3 -m http.server 8080 --bind 127.0.0.1 --directory /tmp/nucleilens-restored/dist
```

The compressed V6 archive SHA256 is
`715fead2b578f285f83ebcc68f5c4fe79677dd337c168009908e3f3c82307e78`.
It contains no account credentials. Use a new empty directory for every drill.
Keep the actual archive/source SHA in the deployment evidence.

## Redeploy the existing public origin

Reuse the existing Site and its source checkout. Retrieve fresh short-lived write
authorization through the connected Sites tool, supply it through protected stdin
to the official site-workflow helper, push/package exact checked output, save that
commit/archive as a version, then deploy that saved version. Check the deployment
status and run the real browser workflow. Never store authorization in this repo
or a command argument. Never replace the Site merely because credentials expired.

For rollback, select a prior verified saved version and deploy that exact version
on the same Site; record the new deployment and recheck the real workflow.
No separate backup production origin has been verified.

## Scientific and review recovery

Rebuild inference from pinned source. Frozen core/graph/evaluation source hashes
are checked by `scripts/check_release.py`. Full held-out results stay in
`evaluation/test/`; no re-evaluation or test-driven tuning is needed for a redeploy.
Unsaved human session state is memory-only. Export label TIFF and review JSON
before refresh; do not describe missing/unexported sessions as recoverable.

The reviewed video is uploaded and attached to Devpost. HD processing and an
anonymous opening sample decoded; a later full-media request hit a sign-in
challenge and was stopped. Browser-player viewing/final submission remain
unverified. Preserve the successful video ID; do not upload again.
Deployments are not evidence of final Devpost submission.

## October 9 fresh restore drill

The exact V6 compressed checksum was verified and extracted into a new temporary
directory. A loopback server on5178 served the restored `dist/`. Actual Chromium
inference,count74, split/merge/undo/TIFF/hash,rerun/cancel and mobile-layout checks
passed. Expanded model QA also passed:68/68 masks, measurements, CSV/TIFF/report
hashes, import rejection and undo. The first QA invocation used the wrong URL
environment variable and hit unopened5173; that failure is retained. The corrected
invocation passed without any application changes.

```bash
NUCLEILENS_DEMO_URL=http://127.0.0.1:5178 node frontend/tests/browser-smoke.mjs
NUCLEILENS_TEST_URL=http://127.0.0.1:5178 node frontend/tests/mask-qa-smoke.mjs
```

Evidence is in `evaluation/checks/recovery-v6-drill.json` and its two browser
reports. This is a local restore drill, not verification of a separate public
backup origin or an offline service worker.
