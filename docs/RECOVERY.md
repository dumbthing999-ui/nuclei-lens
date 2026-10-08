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
python3 -m http.server 8080 --bind 127.0.0.1 --directory frontend/dist
```

Open http://127.0.0.1:8080. Static images, shared scientific code and runtime
libraries are self-hosted. Live inference still runs in the browser. No API keys
are needed. After assets are present, serving the complete build works locally
without an external inference API; this is not a service-worker/offline-cache
promise for a previously visited production page.

## Preserve a release build

The release operator retains an ignored static deployment archive under
`artifacts/nuclei-lens-site.tar.gz`, with `.openai/hosting.json` and complete `dist/`.
Save its SHA256 after the successful build and push. It contains no account
credentials. Extract into a new empty directory, then serve `dist/` as above.
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

Video and final submission remain owner-held gates; deployments are not evidence
of final Devpost submission.
