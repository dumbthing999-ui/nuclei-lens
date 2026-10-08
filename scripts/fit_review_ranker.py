"""A small monotonic risk model; training only, never a probability claim."""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import nnls

from nuclei_lens.evaluate import review_capture

FEATURES = ["graph", "object_disagreement", "count_variation", "shape_flags"]

parser = argparse.ArgumentParser()
parser.add_argument("training", type=Path)
parser.add_argument("validation", type=Path)
parser.add_argument("--out", type=Path, default=Path("evaluation/ranker"))
args = parser.parse_args()
training_summary = json.loads((args.training / "summary.json").read_text())
if training_summary["split"] != "training" or training_summary["partial_partition"]:
    raise SystemExit("Model fitting requires the complete official training partition.")
train = json.loads((args.training / "per-image.json").read_text())
validation_summary = json.loads((args.validation / "summary.json").read_text())
if validation_summary["split"] != "validation":
    raise SystemExit("Model selection requires validation, not test data.")
validation = json.loads((args.validation / "per-image.json").read_text())
matrix = np.array([[tile[name] for name in FEATURES] for record in train for tile in record["region_scores"]])
target = np.array([value for record in train for value in record["tile_error_mass"]])
scale = np.maximum(matrix.std(axis=0), 1e-8)
x = np.column_stack((np.ones(len(matrix)), matrix / scale))
weights, residual = nnls(x, target)
coefficients = weights[1:] / scale
model = {"schema_version": 1, "algorithm": "nonnegative least squares", "features": FEATURES,
         "intercept": float(weights[0]), "coefficients": coefficients.tolist(),
         "training_images": len(train), "training_tiles": len(target), "training_residual_norm": float(residual),
         "training_source_sha256": training_summary["source_sha256"], "config": training_summary["config"],
         "target": "Expected tile FP+FN error mass, not probability, confidence, or human effort", "accepted": False}

loss = np.array([record["error_mass"] for record in validation])
captures = []
for record in validation:
    features = np.array([[tile[name] for name in FEATURES] for tile in record["region_scores"]])
    scores = model["intercept"] + features @ coefficients
    captures.append([review_capture(scores, np.array(record["tile_error_mass"]), k) for k in range(21)])
captures = np.array(captures)
capture = float(captures[:, 4].sum() / loss.sum())
comparator = np.array([r["capture_curves"]["object_disagreement"][4] for r in validation])
rng = np.random.default_rng(20261008)
resamples = rng.integers(0, len(validation), (2000, len(validation)))
denominator = loss[resamples].sum(axis=1)
delta = (captures[:, 4] - comparator)[resamples].sum(axis=1) / denominator
interval = np.percentile(delta, [2.5, 97.5]).tolist()
model["accepted"] = bool(capture >= .48 and interval[0] > 0)
report = {"validation_images": len(validation), "capture_at_20_percent": capture,
          "review_curve": (captures.sum(axis=0) / loss.sum()).tolist(),
          "object_comparator_capture": float(comparator.sum() / loss.sum()),
          "paired_difference": float((captures[:, 4] - comparator).sum() / loss.sum()), "paired_ci95": interval,
          "acceptance_rule": "At least 48% primary error capture at 20% review and positive paired 95% interval versus object disagreement",
          "accepted": model["accepted"], "selection_data": "Validation was already used for segmentation safeguards; only test is held out"}
args.out.mkdir(parents=True, exist_ok=True)
(args.out / "model.json").write_text(json.dumps(model, indent=2) + "\n")
(args.out / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
