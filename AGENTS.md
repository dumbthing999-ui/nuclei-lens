# EurekaDev 2026 Workspace Instructions

## Latest owner steering — October 8, 2026

Keep working autonomously on implementation, UI/UX, evidence, GitHub, deployment,
and Devpost until the practical quality gates pass. **Hold demo video production
and publication** until the owner provides their special instructions. Do not
create video footage, voiceover, a final video, or upload video in the meantime.
The final submission remains gated on its required video and any owner-only legal
attestation. Routine implementation, testing, and reversible publishing are authorized.

## General agent operating rules

- Respect explicit usage budgets and avoid redundant exploration without sacrificing correctness.
- Delegate bounded, high-volume research or checks when a cheaper agent can do them; reserve synthesis and critical review for the lead agent.
- Turn proven repeatable workflows into scoped reusable skills when that clearly helps this workspace.
- Keep persistent preferences in this file and avoid repeating them in prompts.
- Accept mid-run steering and pivot promptly when the owner corrects direction.
- Keep tool reports concise; expose full diagnostics only when they explain a failure.
- Be direct and concise. Point to exact paths and locations when reporting workspace changes.
- Maintain `PROJECT_STATUS.md` and `.progress.md` for multi-step work, recording completed steps, files, blockers, and next actions.
- Quality is the constraint: complete deliverables, exact dependencies/errors, and no placeholders presented as finished work.
- For fixed usage-reset windows, consider a lightweight early scheduled trigger only where an available platform supports it and it genuinely helps; never fake activity or bypass service limits.
- Prefer steer-style follow-up handling so new owner direction supersedes discarded work promptly.
- Keep only relevant tools/plugins active for a task; do not disable global controls without authorization and a concrete need.
- Never change global settings, install broad plugins, disable security, or add credentials without a concrete project need.

These instructions apply to every agent and person working in this workspace. The owner has authorized autonomous, reversible work toward a truthful, competitive EurekaDev 2026 Coding Track submission. Work independently, challenge assumptions with evidence, and keep the owner informed through concise progress updates. Do not wait for routine technical choices.

## Mission and priorities

Optimize for the official judging criteria: Innovation & Creativity, Impact & Relevance, Execution & Technical Quality, and Presentation & Communication (equal weight). Default to the Coding Track. Choose a category only when the project honestly fits it. Focus on one important problem, a distinct technical insight, measured evidence, a reliable demo, and a memorable explanation. Reject generic LLM wrappers and weak ideas early. Do not inflate scores or claims.

Prioritize: eligibility/rules; broken core; innovation; evidence and evaluation; demo reliability; impact proof; UX; video; README and submission; visual polish; optional features. Feature freeze is October 19, 2026. The stated deadline is October 20, 2026, 5:00 PM CDT (October 21 IST); October 20 is for QA and submission verification.

## Official-rule precedence and integrity

Check the latest official EurekaDev Devpost page, rules, resources, updates, discussions, announcements, and gallery before major decisions; refresh them periodically. Rules currently say participants must be high-school students roughly ages 13–19, teams have 1–4 participants, Discord membership is required for prizes, projects must be original, and the video is required and at most four minutes. Coding submissions need a public source repository and README; a live demo is recommended. AI-assisted development is allowed, though the overview discourages AI writing and stresses product quality. Reconfirm all of this against current official sources and retain the source/date in `docs/hackathon/rules-snapshot.md`.

Never plagiarize, copy a competitor, fabricate dates/history/users/interviews/experiments/citations/benchmarks, manipulate engagement, misrepresent AI use, scrape private data, bypass access controls, or claim submission/deployment/account changes without readback evidence. Never expose or commit credentials. If eligibility or a required personal declaration is uncertain, do not guess or attest for the owner; identify the specific gate and continue independent work.

## Evidence-first workflow

1. Inspect the current workspace and preserve useful work. Keep `PROJECT_STATUS.md` and a concise progress tracker current during long work.
2. Capture official rules and account-access state. Archive existing draft text before any authorized edit.
3. Build a sourced competitor matrix and landscape from the complete publicly visible gallery; record visibility limits and re-crawl before freeze.
4. Research significant problems using primary sources where possible. Store URL, publisher, publication/retrieval date, exact claim, citation-ready text, and reliability notes under `research/` and index in `research/SOURCES.md`.
5. Generate and weighted-score at least 25 genuinely different concepts; adversarially review the top five, apply the hard gates, and document the decision and rejected finalists before building.
6. Once the concept passes, create a fresh project repository and document the decision, plan, architecture, data flow, evaluation, innovation, security, limitations, and judge scorecard.
7. Implement one reliable vertical slice; measure it against a meaningful baseline when applicable. Keep demo data clearly labeled and functionality honest.
8. Deliver a polished, accessible live demo, reproducible repository, judge-quality README and Devpost copy, screenshots, and a 3:20–3:45 video (never over four minutes).
9. Run focused checks when needed; do not report tests, security audits, account state, or production health unless actually verified. Keep known risks and next actions explicit.
10. Complete three independent judge simulations (technical, impact/research, skeptical); any official score below 4.5/5 requires improvement. The 19+/20 target and 4.7/category threshold are aspirations, not self-awarded scores.

Required durable artifacts include `docs/hackathon/rules-snapshot.md`, `docs/hackathon/JUDGE_SCORECARD.md`, `docs/hackathon/RED_TEAM.md` (30 concrete criticisms and fixes), `docs/PROJECT_PLAN.md`, `docs/architecture.md`, `docs/INNOVATION.md`, `docs/DECISIONS.md`, `docs/security-review.md`, `docs/TEST_REPORT.md`, `docs/hackathon/category-selection.md`, `research/competitors/competitor-matrix.csv`, `research/competitors/competitive-landscape.md`, `research/idea-selection-report.md`, `research/SOURCES.md`, and `PROJECT_STATUS.md`. Create and maintain these as the work reaches each stage; do not fill them with invented evidence.

## Agent collaboration and tools

Use Antigravity when a second agent helps with bounded research, independent critique, repetitive extraction, or review. The available fast model is `gemini-3.8-flash-medium` (use low for routine extraction and high for synthesis/review). Give agents a narrow task, explicit output path/schema, cite sources, and require uncertainty notes. Review every result before using it. Avoid overlapping edits; delegate research to read-only/structured output unless file ownership is explicit.

Hermes is installed locally. Use it for useful bounded tasks only when its configured model/provider and workspace context are suitable. Its current status showed a custom DeepSeek endpoint and no Gemini API key; do not claim Hermes is using Gemini 3.8 Flash unless verified. Antigravity currently exposes Gemini 3.8 Flash High/Medium/Low. Do not configure global providers or credentials as part of this project without a concrete need. Use Firecrawl or browser tools for public web research where available; use connected Devpost/GitHub tools only after checking authentication and actual readback. Never send external messages unless explicitly authorized.

## Technical and release standards

Prefer a small, explainable architecture. Use typed interfaces where useful, validate input, handle failures, provide accessible responsive states, keep secrets out of Git, pin dependencies where sensible, and document reproducible setup. If data/ML is involved, document source/license, cleaning, splits, baseline, metrics, limitations, bias, and failure modes. Run suitable dependency/static checks on the project's own assets. Maintain a public repository, changelog, security policy, and backup/recovery instructions. Do not make risky production changes after submission.

No deployment, account write, registration, legal attestation, or final submission may be described as complete without verified state. The owner has authorized reversible project changes; credentials, payment, personal disclosures, and irreversible destructive actions remain owner-only gates. Never ask the owner to choose ordinary implementation details.

## Current verified constraints (2026-10-07)

- Public Devpost: `https://eurekadev.devpost.com/`; stated deadline Oct 20, 2026 at 5:00 PM CDT.
- Public rules: `https://eurekadev.devpost.com/rules`; tracks/categories and equal-weight judging are listed there.
- Devpost MCP OAuth calls currently fail before returning account data. Do not claim draft, registration, or account contents were inspected.
- Antigravity tool is available with Gemini 3.8 Flash variants. Hermes CLI exists, but current status showed DeepSeek custom endpoint, OpenAI Codex login, and no Google/Gemini API key.
- This workspace began empty and is not yet a Git repository. Do not assume a draft or GitHub repository exists.

## Project decision (2026-10-08)

- Proceed with **NucleiLens**, a microscopy nuclei-count review tool. Coding Track; Biology/Medical and Environmental Science category. Read `docs/DECISIONS.md`, `docs/PROJECT_PLAN.md`, and `docs/architecture.md` before implementation.
- Implement sparse object correspondence graphs across segmentation sensitivity runs to identify count-changing ambiguities and prioritize human review. Known uncertainty/topology/segmentation methods are prior art; make no scientific-first or accuracy claim without evidence.
- Prioritize the offline graph/evaluation vertical slice. Validate the declared equal-review-budget comparison before product polish; continue/pivot gate is October 10.
- BBBC039v1 official record documents CC0, instance annotations, and official splits. Ground truth is evaluation-only and must not enter inference.
- Age/high-school eligibility and Discord membership are owner-confirmed. Devpost draft/registration remain unverified.
- A fresh local Git repository was initialized on `main` on October 8. No commits or public remote have been created yet; the October 7 empty-workspace observation above is historical.

## Verified progress superseding historical account/build observations — October 8

The functional NucleiLens browser implementation and all50 frozen test records exist. Default object-disagreement ordering was selected on validation; graph superiority and the NNLS model failed their gates. Preserve those negative results. Public Site: https://nuclei-lens.dumbthing999.chatgpt.site. Public GitHub repository: https://github.com/dumbthing999-ui/nuclei-lens; verify exact source/CI state in PROJECT_STATUS.md. Fresh owner-supplied authentication now succeeds through the protected Hermes environment. Authenticated whoami/project listing, fresh EurekaDev draft creation and readback are verified: NucleiLens project1470185/submission1224432, state Draft, no video. Initial draft is archived before future edits. Public thumbnail and three gallery uploads succeeded. Never print upload instructions or nested connector responses: they may embed bearer credentials. Video hold remains in force.


Explicit human-confirmed mask replacement, conflict rejection, undo and uint32 TIFF/SHA256 audit are implemented and locally checked. Tally entries remain separate. Native27/frontend10 tests pass. CI repair PR1 merged; mask feature CI found a missing Node type declaration, now pinned and checked with a clean npm install. Verify the next actual remote CI before merging/deploying the feature. Do not change frozen core/graph/evaluate hashes or tune on test results.


## Latest verified release/account state — October8,2026

PR2 merged; v0.1.0 prerelease points to c4a73d7b7f36d322ad04a41ab531106475c7a684,
exact tree of green CI37745742321. PublicV3 mask workflow/automated accessibility
pass. Devpost update_project auto-published project page; EurekaDev submitted_at
remains null and video absent. Fresh public rendered copy/media/links verified.
Required contact-email disclosure remains owner-only. BBBC038 raw-image profile
has539 property candidates from670 fields; no annotations/inference/external result.
Preserve frozen scientific source and video hold. See latest PROJECT_STATUS.md.
