"""Export real precomputed training examples, never substitute fake outputs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from nuclei_lens.core import analyze
from nuclei_lens.data import Dataset
from nuclei_lens.evaluate import instance_metrics
from nuclei_lens.raster import serialize

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "frontend/public/samples"
target.mkdir(parents=True, exist_ok=True)
examples = [(0, "First training field", "First image in the official training manifest."),
            (1, "Dense field", "Second training image; many adjacent nuclei."),
            (6, "Harder field", "Lowest baseline F1 among the first eight training images; included to expose a failure case.")]
manifest = []
with Dataset() as dataset:
    for index, title, note in examples:
        filename = dataset.filenames("training")[index]
        result = analyze(dataset.image(filename))
        metrics = instance_metrics(result["masks"][0], dataset.annotations(filename))
        sample_id = f"training-{index + 1:03d}"
        (target / f"{sample_id}.json").write_text(json.dumps(serialize(result)))
        (target / f"{sample_id}.tif").write_bytes(dataset.image_bytes(filename))
        manifest.append({"id": sample_id, "title": title, "filename": filename.replace(".png", ".tif"),
                         "note": note, "analysis_url": f"/samples/{sample_id}.json",
                         "image_url": f"/samples/{sample_id}.tif", "reference_count": metrics["annotation_count"],
                         "f1": metrics["f1"]})
(target / "manifest.json").write_text(json.dumps({"dataset": "BBBC039", "license": "CC0",
    "source": "https://bbbc.broadinstitute.org/BBBC039", "mode": "Real precomputed reference runs; rerun locally in browser to verify.",
    "samples": manifest}, indent=2) + "\n")
engine = ROOT / "frontend/public/engine/nuclei_lens"
engine.mkdir(parents=True, exist_ok=True)
for name in ["__init__.py", "core.py", "graph.py", "raster.py"]:
    shutil.copyfile(ROOT / "src/nuclei_lens" / name, engine / name)
print(f"Exported {len(manifest)} real training samples and shared analysis code.")
