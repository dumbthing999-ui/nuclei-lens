"""Score actual exported JSON only; references never belong in the served root.

JSON identity/consent/timestamps are self-reported, not authenticated evidence.
Private seals detect corruption relative to a trusted seal, not malicious resealing.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from hashlib import sha256
from io import BytesIO
from pathlib import Path

from prepare_reader_exercise import canonical, digest, export_contract


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result

    if Path(path).stat().st_size > 10 * 1024 * 1024:
        raise ValueError("JSON exceeds 10 MB limit")
    return json.loads(
        Path(path).read_text(),
        object_pairs_hook=unique,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Nonfinite JSON")),
    )


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def text(value):
    return isinstance(value, str) and len(value) <= 500


def stamp(value):
    require(isinstance(value, str), "Invalid timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None and parsed.utcoffset().total_seconds() == 0, "Timestamp must be UTC")
    return parsed


def validate_export(record, protocol, protocol_hash, allow_synthetic):
    contract = export_contract()
    require(
        isinstance(record, dict) and set(record) == set(contract["required_export_keys"]),
        "Unexpected export keys",
    )
    require(type(record["schema_version"]) is int and record["schema_version"] == 1, "Invalid schema")
    require(record["protocol_hash"] == protocol_hash, "Protocol mismatch")
    participant = record["participant_id"]
    require(isinstance(participant, str) and participant in protocol["assignments"], "Unexpected participant")
    require(type(record["synthetic_test"]) is bool, "synthetic_test must be boolean")
    require(
        not record["synthetic_test"] or allow_synthetic,
        "Synthetic export rejected; use --allow-synthetic for validation",
    )
    require(record["experience_band"] in contract["experience_band"], "Invalid experience")
    require(record["retention_choice"] in contract["retention_choice"], "Invalid retention")
    require(
        record["consent_acknowledged"] is True,
        "Consent acknowledgement required; not independently authenticated",
    )
    require(isinstance(record["tasks"], list) and len(record["tasks"]) <= 4, "Invalid tasks")
    expected = {task["task_id"]: task for task in protocol["assignments"][participant]}
    seen = set()
    for task in record["tasks"]:
        require(
            isinstance(task, dict) and set(task) == set(contract["required_task_keys"]),
            "Unexpected task keys",
        )
        task_id = task["task_id"]
        require(
            isinstance(task_id, str) and task_id in expected and task_id not in seen,
            "Duplicate/unexpected task",
        )
        seen.add(task_id)
        for key, value in expected[task_id].items():
            require(canonical(task[key]) == canonical(value), f"Assignment mismatch: {key}")
        require(stamp(task["ended_at"]) >= stamp(task["started_at"]), "Reversed timestamps")
        require(integer(task["elapsed_ms"], 0, 86400000), "Invalid elapsed time")
        interruptions = task["visibility_interruptions_ms"]
        require(
            isinstance(interruptions, list)
            and all(integer(x, 0, task["elapsed_ms"]) for x in interruptions)
            and interruptions == sorted(interruptions),
            "Invalid visibility offsets",
        )
        require(
            task["status"] in contract["task_status"]
            and text(task["reason"])
            and text(task["comprehension"]),
            "Invalid task status/text",
        )
        require(task["status"] == "completed" or bool(task["reason"].strip()), "Incomplete task needs reason")
        require(
            isinstance(task["regions"], list) and len(task["regions"]) == 4,
            "Exactly four region records required",
        )
        tiles = set()
        for region in task["regions"]:
            require(
                isinstance(region, dict) and set(region) == set(contract["required_region_keys"]),
                "Unexpected region keys",
            )
            tile = region["tile_id"]
            require(
                integer(tile, 0, 19) and tile in task["tile_ids"] and tile not in tiles,
                "Unexpected/duplicate tile",
            )
            tiles.add(tile)
            require(integer(region["baseline_count"], 0, 1000), "Invalid baseline count")
            require(
                region["entered_count"] is None or integer(region["entered_count"], 0, 1000), "Invalid count"
            )
            require(
                region["uncertainty"] is None or integer(region["uncertainty"], 0, 3), "Invalid uncertainty"
            )
            require(
                type(region["confirmed"]) is bool
                and region["status"] in contract["region_status"]
                and text(region["reason"]),
                "Invalid region status",
            )
            if region["status"] == "completed":
                require(
                    region["confirmed"]
                    and region["entered_count"] is not None
                    and region["uncertainty"] is not None,
                    "Incomplete confirmed region",
                )
            else:
                require(not region["confirmed"], "Incomplete region cannot be confirmed")
                require(
                    region["status"] != "unresolved" or bool(region["reason"].strip()),
                    "Unresolved region needs reason",
                )
                require(task["status"] != "completed", "Completed task has incomplete region")
    return record


def score(private_root, served_root, export_paths, allow_synthetic=False):
    require(bool(export_paths), "Actual export paths required before loading references")
    private, served = Path(private_root), Path(served_root)
    seal = load(private / "seal.json")
    require(
        set(path.name for path in private.iterdir()) == set(seal["private_files"]) | {"seal.json"},
        "Unexpected private files",
    )
    for name, expected in seal["private_files"].items():
        require(
            Path(name).name == name and sha256((private / name).read_bytes()).hexdigest() == expected,
            "Private integrity mismatch",
        )
    require(
        set(path.name for path in served.iterdir()) == set(seal["served_files"]), "Unexpected served files"
    )
    for name, expected in seal["served_files"].items():
        require(
            Path(name).name == name and sha256((served / name).read_bytes()).hexdigest() == expected,
            "Served integrity mismatch",
        )
    protocol = load(private / "protocol.json")
    require(digest(protocol) == seal["protocol_hash"], "Private protocol mismatch")
    records = [
        validate_export(load(path), protocol, seal["protocol_hash"], allow_synthetic) for path in export_paths
    ]
    require(
        len({record["participant_id"] for record in records}) == len(records), "Duplicate participant export"
    )
    require(
        len({record["synthetic_test"] for record in records}) == 1,
        "Cannot mix synthetic and non-synthetic exports",
    )
    for record in records:
        for task in record["tasks"]:
            asset = load(served / f"{task['field_id']}-{task['arm_id']}.json")
            baselines = {region["id"]: region["baseline_count"] for region in asset["regions"]}
            for region in task["regions"]:
                require(region["baseline_count"] == baselines[region["tile_id"]], "Tampered baseline count")
    require(
        all(record["retention_choice"] != "delete" for record in records),
        "Withdrawn export: remove/delete according to operator retention procedure before scoring remaining exports; no files purged by scorer",
    )
    # Decode annotation references ONLY after all supplied exports pass validation.
    import numpy as np
    from PIL import Image
    from skimage.measure import label

    from nuclei_lens.core import tile_counts

    participants = []
    for record in records:
        entry = {
            "participant_id": record["participant_id"],
            "synthetic_test": record["synthetic_test"],
            "retention_choice": record["retention_choice"],
            "experience_band": record["experience_band"],
            "tasks": [],
            "descriptive_by_arm": {},
        }
        supplied = {task["task_id"]: task for task in record["tasks"]}
        for assignment in protocol["assignments"][record["participant_id"]]:
            task = supplied.get(assignment["task_id"])
            field = assignment["field_id"]
            asset = load(served / f"{field}-{assignment['arm_id']}.json")
            baselines = {region["id"]: region["baseline_count"] for region in asset["regions"]}
            with Image.open(BytesIO((private / f"{field}.png").read_bytes())) as image:
                reference = label(np.asarray(image)[..., 0], connectivity=2, background=0).astype(np.int32)
            counts = tile_counts(reference)
            if task is None:
                task = {
                    **assignment,
                    "status": "missing",
                    "regions": [
                        {
                            "tile_id": tile,
                            "baseline_count": baselines[tile],
                            "entered_count": None,
                            "uncertainty": None,
                            "confirmed": False,
                            "status": "not_started",
                            "reason": "Task export missing",
                        }
                        for tile in assignment["tile_ids"]
                    ],
                }
            result = {**task, "regions": []}
            for region in task["regions"]:
                tile = region["tile_id"]
                require(region["baseline_count"] == baselines[tile], "Tampered baseline count")
                scored = {
                    **region,
                    "reference_count": int(counts[tile]),
                    "absolute_error": None,
                    "baseline_absolute_error": abs(region["baseline_count"] - int(counts[tile])),
                    "error_reduction": None,
                    "wrong_direction": None,
                }
                if region["status"] == "completed":
                    before = abs(region["baseline_count"] - int(counts[tile]))
                    after = abs(region["entered_count"] - int(counts[tile]))
                    scored.update(
                        absolute_error=after, error_reduction=before - after, wrong_direction=after > before
                    )
                result["regions"].append(scored)
            entry["tasks"].append(result)
        for arm in ("A", "B"):
            tasks = [task for task in entry["tasks"] if task["arm_id"] == arm]
            regions = [region for task in tasks for region in task["regions"]]
            observed = [region for region in regions if region["absolute_error"] is not None]
            complete = all(task["status"] == "completed" for task in tasks) and len(observed) == 8

            def mean(values):
                return sum(values) / len(values) if values else None

            entry["descriptive_by_arm"][arm] = {
                "arm_data_complete": complete,
                "observed_region_count": len(observed),
                "scheduled_region_count": 8,
                "mean_absolute_local_count_error": mean([r["absolute_error"] for r in observed])
                if complete
                else None,
                "same_assigned_tile_baseline_mae": mean([r["baseline_absolute_error"] for r in regions]),
                "mean_baseline_minus_entered_error_reduction": mean([r["error_reduction"] for r in observed])
                if complete
                else None,
                "partial_observed_only": None
                if complete
                else {
                    "final_mae": mean([r["absolute_error"] for r in observed]),
                    "baseline_mae_same_observed_tiles": mean(
                        [r["baseline_absolute_error"] for r in observed]
                    ),
                    "mean_error_reduction": mean([r["error_reduction"] for r in observed]),
                    "caveat": "Incomplete selected observations; not a complete arm or paired estimate.",
                },
                "completed_tasks": sum(task["status"] == "completed" for task in tasks),
                "missing_tasks": sum(task["status"] == "missing" for task in tasks),
                "failed_tasks": sum(task["status"] == "failed" for task in tasks),
                "aborted_tasks": sum(task["status"] == "aborted" for task in tasks),
                "unresolved_regions": sum(r["status"] == "unresolved" for r in regions),
                "not_started_regions": sum(r["status"] == "not_started" for r in regions),
                "elapsed_ms_all_supplied_tasks": sum(task.get("elapsed_ms", 0) for task in tasks),
            }
        entry["paired_data_complete"] = all(
            arm["arm_data_complete"] for arm in entry["descriptive_by_arm"].values()
        )
        entry["paired_descriptive_B_minus_A"] = None
        if entry["paired_data_complete"]:
            arms = entry["descriptive_by_arm"]
            entry["paired_descriptive_B_minus_A"] = {
                key: arms["B"][key] - arms["A"][key]
                for key in (
                    "mean_absolute_local_count_error",
                    "same_assigned_tile_baseline_mae",
                    "mean_baseline_minus_entered_error_reduction",
                )
            }
        participants.append(entry)
    synthetic = records[0]["synthetic_test"]
    return {
        "schema_version": 1,
        "protocol_hash": seal["protocol_hash"],
        "synthetic_test": synthetic,
        "evidence_label": "SYNTHETIC SOFTWARE TEST — NOT HUMAN OBSERVATIONS"
        if synthetic
        else "SELF-REPORTED EXPORTS — HUMAN IDENTITY/CONSENT/TIMESTAMPS NOT AUTHENTICATED",
        "limitations": "Training/development fields. Participant-level descriptive records only; no significance, success threshold, population or human-benefit inference. Incomplete observations remain explicit; tiles are not participants. Seal is a local integrity anchor, not a signature.",
        "metric_roles": {
            "primary": "Final local-count MAE on complete assigned arm data",
            "secondary": "Same-assigned-tile baseline MAE and baseline-minus-entered absolute error reduction; declared before sessions, no metric switching or success threshold",
        },
        "selection_difficulty_caveat": "Arms select different tiles and each participant sees different fields between arms. Assisted selection may target initially harder regions; raw final MAE differences are not an isolated causal effect of assistance. Secondary reduction is descriptive, not mask accuracy or proof of benefit. Partial observations are separately labeled; no pooling tiles as people.",
        "participants": participants,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", required=True)
    parser.add_argument("--served", required=True)
    parser.add_argument("--exports", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--allow-synthetic", action="store_true")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    require(not output.exists(), "Output must be new")
    require(
        not any(
            root.resolve() == output or root.resolve() in output.parents
            for root in (Path(args.private), Path(args.served))
        ),
        "Score output must be outside bundle roots",
    )
    output.write_bytes(
        canonical(score(args.private, args.served, args.exports, args.allow_synthetic)) + b"\n"
    )


if __name__ == "__main__":
    main()
