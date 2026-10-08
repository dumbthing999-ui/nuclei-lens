"""Render complete fixed-budget curves and intervals from saved experiments."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parents[1]
output = root / "evaluation/figures"
output.mkdir(exist_ok=True)
colors = {
    "object_disagreement": "#2255db",
    "graph": "#d97822",
    "pixel_disagreement": "#65758e",
    "count_variation": "#567c53",
    "shape_flags": "#9a699a",
    "random": "#aaaeb8",
}
fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), layout="constrained")
for axis, split, folder in zip(
    axes,
    ["Validation (development)", "Test (frozen)"],
    ["experiments/saturation-gated-validation", "test"],
    strict=True,
):
    summary = json.loads((root / "evaluation" / folder / "summary.json").read_text())
    for name, values in summary["methods"].items():
        axis.plot(
            np.arange(21) * 5,
            np.array(values["review_curve"]) * 100,
            label=name.replace("_", " "),
            color=colors[name],
            linewidth=2.2 if name == "object_disagreement" else 1.5,
        )
    axis.set(
        xlabel="Regions reviewed (% of 20 fixed tiles)",
        ylabel="Annotated FP+FN error mass captured (%)",
        title=f"{split} · {summary['n_images']} fields",
        xlim=(0, 100),
        ylim=(0, 100),
    )
    axis.axvline(20, linestyle=":", color="#8690a2", linewidth=1)
    axis.grid(alpha=0.18)
axes[1].legend(fontsize=8, loc="lower right")
fig.savefig(output / "review-curves.png", dpi=180)
fig.savefig(output / "review-curves.svg")
plt.close(fig)
summary = json.loads((root / "evaluation/test/summary.json").read_text())
fig, axis = plt.subplots(figsize=(9, 4.2), layout="constrained")
names = list(colors)
values = np.array([summary["methods"][name]["capture_at_20_percent"] for name in names]) * 100
intervals = np.array([summary["methods"][name]["capture_ci95"] for name in names]) * 100
axis.barh([n.replace("_", " ") for n in names], values, color=[colors[name] for name in names], alpha=0.85)
axis.errorbar(
    values,
    np.arange(len(names)),
    xerr=np.array([values - intervals[:, 0], intervals[:, 1] - values]),
    fmt="none",
    ecolor="#172333",
    capsize=3,
)
axis.invert_yaxis()
axis.set(
    xlabel="Annotated error mass captured (%) · 4/20 tiles",
    title="Frozen test · 50 fields · image-bootstrap 95% intervals",
    xlim=(0, 65),
)
axis.grid(axis="x", alpha=0.15)
for row, value in enumerate(values):
    axis.text(value + 2, row, f"{value:.1f}%", va="center", fontsize=9)
fig.savefig(output / "test-budget-comparison.png", dpi=180)
fig.savefig(output / "test-budget-comparison.svg")
plt.close(fig)
print("Rendered complete curves and uncertainty intervals from saved records.")
