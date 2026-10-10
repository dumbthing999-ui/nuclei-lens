"""Build an offline reader bundle; never alters frozen inference or assessments.

Run with --dataset PATH --served PATH --private PATH. Both output roots must be
new, disjoint and outside each other. Serve ONLY --served, never the repository.
"""

from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def write_json(path, value):
    path.write_bytes(canonical(value) + b"\n")


def ordered(seed, domain, items):
    return sorted(items, key=lambda item: (digest([seed, domain, item]), item))


def assignments(fields, seed):
    """Fixed field order balances arm and period; tile selection is field-specific."""
    result = {}
    for number in range(1, 7):
        participant = f"P{number:02d}"
        tasks = []
        for index, (field_id, field) in enumerate(fields.items()):
            assisted = (index >= 2) == (number % 2 == 1)
            arm = "B" if assisted else "A"
            regions = field["regions"]
            tie = ordered(seed, field_id + ":tie", list(range(20)))
            rank = {tile: index for index, tile in enumerate(tie)}
            tiles = (
                sorted(
                    range(20),
                    key=lambda tile: (-regions[tile]["comparators"]["object_disagreement"], rank[tile]),
                )[:4]
                if assisted
                else ordered(seed, field_id + ":control", list(range(20)))[:4]
            )
            tiles = ordered(seed, field_id + ":presentation:" + arm, tiles)
            task = {
                "task_id": f"T{index + 1:02d}",
                "order": index + 1,
                "field_id": field_id,
                "arm_id": arm,
                "tile_ids": tiles,
                "input_hash": field["input_hash"],
                "field_hash": field["field_hash"],
                "config_hash": field["config_hash"],
            }
            task["assignment_hash"] = digest(task)
            tasks.append(task)
        result[participant] = tasks
    return result


def export_contract():
    return {
        "schema_version": 1,
        "required_export_keys": [
            "schema_version",
            "protocol_hash",
            "participant_id",
            "synthetic_test",
            "experience_band",
            "retention_choice",
            "consent_acknowledged",
            "tasks",
        ],
        "required_task_keys": [
            "task_id",
            "order",
            "field_id",
            "arm_id",
            "tile_ids",
            "input_hash",
            "field_hash",
            "config_hash",
            "assignment_hash",
            "started_at",
            "ended_at",
            "elapsed_ms",
            "visibility_interruptions_ms",
            "status",
            "reason",
            "regions",
            "comprehension",
        ],
        "required_region_keys": [
            "tile_id",
            "baseline_count",
            "entered_count",
            "uncertainty",
            "confirmed",
            "status",
            "reason",
        ],
        "task_status": ["completed", "aborted", "failed"],
        "region_status": ["completed", "unresolved", "not_started"],
        "experience_band": ["basic", "experienced", "unspecified"],
        "retention_choice": ["retain", "delete"],
        "bounds": {
            "count": [0, 1000],
            "uncertainty": [0, 3],
            "elapsed_ms": [0, 86400000],
            "text_max_length": 500,
        },
        "nullable": ["region.entered_count", "region.uncertainty"],
        "timing": "UTC ISO8601 timestamps; monotonic elapsed_ms begins after asset loading. No automatic pause. Visibility interruptions are monotonic offsets, nondecreasing within elapsed_ms.",
        "incomplete": "Export may omit unstarted tasks; scorer reports these as missing. Supplied tasks contain all four regions. Completed regions require count, uncertainty and confirmation. Completed tasks require four completed regions; other statuses require a reason.",
        "synthetic_policy": "synthetic_test is a required boolean. UI ?test=1 must visibly label software testing and export true. Default scorer rejects true; --allow-synthetic labels validation only.",
        "evidence_limit": "Identity, consent and timestamps are self-reported JSON, not independently authenticated human evidence.",
    }


def validate_frozen(root):
    frozen = json.loads((root / "evaluation/frozen/protocol.json").read_text())
    config = json.loads((root / "evaluation/frozen/config.json").read_text())
    if config != frozen["config"]:
        raise ValueError("Frozen configuration mismatch")
    for name, expected in frozen["source_sha256"].items():
        if sha256((root / "src/nuclei_lens" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Frozen source mismatch: " + name)
    return config


def prepare(dataset_root, served_root, private_root, seed="nucleilens-reader-v1", *, assets_directory=None):
    from nuclei_lens.core import Config, analyze
    from nuclei_lens.data import Dataset
    from nuclei_lens.raster import serialize

    served, private = Path(served_root).resolve(), Path(private_root).resolve()
    if served == private or served in private.parents or private in served.parents:
        raise ValueError("Output roots must be disjoint")
    if served.exists() or private.exists():
        raise ValueError("Output roots must be new")
    if ROOT == served or ROOT in served.parents or ROOT == private or ROOT in private.parents:
        raise ValueError("Generated artifacts must be outside the worktree")
    if assets_directory is None:
        raise ValueError("Explicit UI assets directory required before sealing")
    assets = Path(assets_directory)
    ui = {}
    for name in ("index.html", "app.js", "style.css"):
        path = assets / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing regular UI asset: " + name)
        ui[name] = path.read_bytes()
    config = validate_frozen(ROOT)
    config_hash = digest(config)
    sources = {
        str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
        for path in [
            ROOT / "src/nuclei_lens" / name
            for name in ("core.py", "graph.py", "evaluate.py", "raster.py", "data.py", "__init__.py")
        ]
        + [
            ROOT / "scripts/prepare_reader_exercise.py",
            ROOT / "scripts/score_reader_exercise.py",
            ROOT / "evaluation/frozen/config.json",
            ROOT / "evaluation/frozen/protocol.json",
        ]
    }
    sources.update({"reader-exercise/" + name: sha256(payload).hexdigest() for name, payload in ui.items()})
    fields, mapping, references, practice = {}, {}, {}, None
    with Dataset(dataset_root) as dataset:
        for position in (3, 4, 5, 6, 8):
            filename = dataset.filenames("training")[position - 1]
            raw = dataset.image_bytes(filename)
            analysis = serialize(analyze(dataset.image(filename), Config(**config)))
            field_id = f"F{position - 2:02d}" if position != 8 else "Q01"
            analysis["field_hash"] = sha256(raw).hexdigest()
            analysis["config_hash"] = config_hash
            mapping[field_id] = {
                "position": position,
                "filename": filename,
                "field_hash": analysis["field_hash"],
                "input_hash": analysis["input_hash"],
            }
            references[field_id] = dataset.masks.read("masks/" + filename)
            if position == 8:
                practice = analysis
            else:
                fields[field_id] = analysis
    allocation = assignments(fields, seed)
    protocol = {
        "schema_version": 1,
        "seed": seed,
        "sources": sources,
        "config_hash": config_hash,
        "fields": mapping,
        "assignments": allocation,
        "arm_decoding": {"A": "control", "B": "assisted"},
        "reference_hashes": {key: sha256(value).hexdigest() for key, value in references.items()},
        "disclosure": "Official training/development fields, all retained. No human sessions or benefit evidence. Four tiles are not equal human effort. Concrete seeded ties differ from expected-tie benchmark capture.",
        "mechanics": export_contract(),
    }
    protocol_hash = digest(protocol)
    served.mkdir(parents=True)
    private.mkdir(parents=True, mode=0o700)
    for name, payload in ui.items():
        (served / name).write_bytes(payload)
    public = {
        "schema_version": 1,
        "protocol_hash": protocol_hash,
        "config_hash": config_hash,
        "source_hash": digest(sources),
        "disclosure": protocol["disclosure"],
        "assignments": allocation,
        "practice_id": "Q01",
    }
    write_json(served / "manifest.json", public)
    write_json(served / "export-contract.json", export_contract())
    for field_id, analysis in {**fields, "Q01": practice}.items():
        for arm in ("A", "B"):
            asset = {
                "field_id": field_id,
                "arm_id": arm,
                "input_hash": analysis["input_hash"],
                "field_hash": analysis["field_hash"],
                "config_hash": config_hash,
                "width": analysis["width"],
                "height": analysis["height"],
                "image_png": analysis["image_png"],
                "baseline_outline_png": analysis["outline_pngs"][0],
                "regions": [
                    {key: region[key] for key in ("id", "bbox", "baseline_count")}
                    for region in analysis["regions"]
                ],
            }
            if arm == "B":
                asset["alternative_outline_pngs"] = analysis["outline_pngs"][1:]
                for dest, region in zip(asset["regions"], analysis["regions"], strict=True):
                    dest.update({key: region[key] for key in ("events", "run_counts")})
            write_json(served / f"{field_id}-{arm}.json", asset)
    for field_id, payload in references.items():
        (private / f"{field_id}.png").write_bytes(payload)
    write_json(private / "protocol.json", protocol)
    write_json(
        private / "seal.json",
        {
            "protocol_hash": protocol_hash,
            "private_files": {
                path.name: sha256(path.read_bytes()).hexdigest() for path in sorted(private.iterdir())
            },
            "served_files": {
                path.name: sha256(path.read_bytes()).hexdigest() for path in sorted(served.iterdir())
            },
        },
    )
    return public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--served", required=True)
    parser.add_argument("--private", required=True)
    parser.add_argument("--seed", default="nucleilens-reader-v1")
    parser.add_argument("--assets-directory", required=True)
    args = parser.parse_args()
    prepare(args.dataset, args.served, args.private, args.seed, assets_directory=args.assets_directory)


if __name__ == "__main__":
    main()
