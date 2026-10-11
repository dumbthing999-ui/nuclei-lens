### Technical Hackathon Judge Evaluation: NucleiLens

**Context & Scope**: Independent technical review based strictly on [README.md](../../../README.md), [docs/INNOVATION.md](../../INNOVATION.md), [docs/architecture.md](../../architecture.md), [docs/OPTIONAL_MODELS.md](../../OPTIONAL_MODELS.md), and [docs/hackathon/JUDGE_SCORECARD.md](../JUDGE_SCORECARD.md).

---

### Category Scores & Breakdown (1–5)

| Category | Score | Verified Evidence Item | Key Limitation |
| :--- | :---: | :--- | :--- |
| **Innovation** | **3.7 / 5** | Sparse bipartite overlap graphs track instances across 9 controlled sensitivity variations to expose opposing split/merge events that conceal count changes when aggregate totals match (demonstrated by the 74→75→74 witness). | Underlying segmentation (watershed, thresholding, morphological distance) is established prior art; graph ranking underperformed simple object disagreement on error capture (38.4% vs. 44.0% on validation), making graphs an explanatory feature rather than an accuracy driver. |
| **Impact** | **3.3 / 5** | On the 50 frozen held-out test fields (BBBC039), the preselected object-disagreement queue captured 45.8% of instance FP+FN error mass within a 20% review budget (vs. 20.0% expected random); confirmed at 45.7% across 496 BBBC038 fields. | Review efficiency is evaluated against synthetic fixed-tile budgets on reference masks; real reader time savings, user productivity, and downstream biological utility have not been measured with consenting participants. |
| **Technical Execution** | **4.6 / 5** | Full device-local scientific pipeline running the exact numerical Python core via Pyodide in a dedicated Web Worker, with bounded TIFF decoding, conflict-checked mask replacement, exact undo, little-endian uint32 TIFF export, and SHA-256 provenance logging. | Cold-start latency requires downloading ~39 MB of WebAssembly/Pyodide scientific assets; verified alignment of imported external label masks relies on subjective user acknowledgment rather than automated verification. |
| **Presentation** | **4.2 / 5** | Exemplary scientific honesty and clarity: negative findings (graph ranking underperformance, rejected NNLS ranker) are openly reported, accompanied by a reproducible 74→75→74 interactive workflow and an attached 3:35 HD video walk-through. | High conceptual density requires bioimage informatics domain knowledge to interpret the trade-offs; full anonymous end-to-end player playback across diverse viewer regions remains unverified. |

**Total Score**: **15.8 / 20**

---

### Execution of Real Segmentation Models (Web App vs. Local CLI/Import)

* **Within the Web App**: Deep neural segmentation models **do not** run in the browser. The web application runs only the deterministic classical numerical pipeline (Otsu thresholding, distance transform, watershed, and bipartite overlap graphs) locally via Pyodide/WebAssembly.
* **Via Optional Local CLI / Import**: Real deep learning models ([Cellpose](../../OPTIONAL_MODELS.md#L38) and [StarDist](../../OPTIONAL_MODELS.md#L39)) execute strictly through an optional offline CLI script ([`scripts/run_model_masks.py`](../../OPTIONAL_MODELS.md#L35)) in an isolated Python 3.12 environment using CPU PyTorch and TensorFlow. Their outputs are exported as uncompressed unsigned integer label TIFFs with SHA-256 provenance files, which the browser app then **imports** for overlay comparison, geometric measurements, and conflict-checked component editing. The web app also provides bundled precomputed runs for the first training field.
