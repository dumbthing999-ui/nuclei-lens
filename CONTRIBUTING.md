# Contributing

Read `AGENTS.md`, `PROJECT_STATUS.md`, and `docs/DECISIONS.md` before work.
Use Python 3.14 and Node 26. Install with `pip install -e '.[dev]'` and
`npm ci --prefix frontend`. Keep changes small and explain their evidence.

Before proposing a change, run `pytest`, `ruff check src tests scripts`,
`npm test --prefix frontend`, and `npm run build --prefix frontend`.
For changed analysis code, regenerate shared browser code and samples with
`python scripts/export_samples.py` after downloading the verified public dataset.
Keep annotations outside inference. Use training/validation for development;
held-out test results must identify the frozen protocol and source hash.

Do not add credentials, patient images, dataset archives, unverified scientific
claims, model APIs, or fabricated evaluation results. Label synthetic test
fixtures and oracle simulations. Security issues belong in a private report;
see `SECURITY.md`. This prototype is not a diagnostic product.
