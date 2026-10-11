# Current-state AI judge simulations — October 12, 2026

Three role-specific Gemini 3.8 Flash reviews were run in separate contexts
against the current public README, project status, technical/evaluation documents,
and Devpost draft. They did not conduct a live browser session, inspect hidden
submission fields, or watch the complete video. These are AI simulations, not
official scores or independent human judges.

| Criterion | Technical | Research/Impact | Skeptical | Mean | Shared concern |
|---|---:|---:|---:|---:|---|
| Innovation | 3.7 | 3.7 | 3.6 | 3.67 | Methods are established prior art; graph ranking did not beat object disagreement. |
| Impact & Relevance | 3.3 | 3.3 | 3.3 | 3.30 | No observed reader sessions or measured human benefit. |
| Technical Execution | 4.6 | 4.5 | 4.6 | 4.57 | Strong reproducibility; limited image domain, local model CLI, and judgment-based mask alignment. |
| Presentation | 4.2 | 4.2 | 4.2 | 4.20 | Strong same-count demo; dense caveats and complete anonymous video playback remain concerns. |
| **Total / 20** | **15.8** | **15.7** | **15.7** | **15.73** | Internal 19+/20 aspiration is not met. |

Raw role reports: [technical](technical.md), [research/impact](research-impact.md),
and [skeptical](skeptical.md).

## Convergent finding

The strongest memorable moment is the real-data 74 → 75 → 74 workflow: a split
and merge can offset each other in the total while changing object assignments.
The evidence supports a narrow audit-first workflow distinction; it does not
establish a new segmentation algorithm, universal accuracy, or biological
identity. The preselected object-disagreement queue captured 45.8% of annotated
FP+FN error mass on the frozen 50-field test at a 20% tile budget. That is a
reference-based simulation, not observed reviewer benefit.

## Review corrections and actions

- All reviewers agree that human benefit remains unmeasured. The prepared reader
  comparison cannot be run without consenting microscopy readers. No participant
  data or benefit claim is invented.
- The web app runs its classical pipeline locally. Actual Cellpose and StarDist
  inference is supported by the optional local CLI; the browser imports bundled
  predictions or user-produced label TIFFs. Do not describe neural inference as
  browser-native.
- External-mask alignment remains a visual human judgment with full-field
  inspection and explicit acknowledgment. The reviews' suggestion to add an
  automatic registration threshold is not adopted: no validated threshold or
  representative alignment benchmark supports safe automatic acceptance.
- The suggested hybrid ranker is not adopted. It would be a new hypothesis that
  needs a predeclared protocol and untouched evaluation; do not tune or select a
  new method against the already-used frozen test.
- Video/player availability concerns are retained. Do not re-upload or bypass
  access controls; the existing YouTube ID and verified GitHub backup remain.
- The phrase “biological measurement is broken” is present in the uploaded
  captions at 0:06. The current Devpost copy qualifies it as a possible
  object-level segmentation mismatch, not a demonstrated downstream outcome;
  preserve that qualification. The approximately39MB runtime is a documented
  cold-start cost for on-device reruns; the precomputed sample keeps the first
  demo path available without that model-runtime download.
- The reviews' broader claims about capabilities in CellProfiler, ImageJ, or
  competing consensus tools were not independently sourced in these simulations
  and are not adopted as factual comparison claims.
- Criticism of dense caveats is useful for future copy editing, but no disclaimer
  is removed without checking whether that would make the public claims less
  accurate.

These reviews do not raise or replace the official judging score. The priority
remains consented reader evidence, if participants become available; otherwise
keep impact and reader utility explicitly unproven.
