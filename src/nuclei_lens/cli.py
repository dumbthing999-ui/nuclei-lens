"""Local analysis/evaluation entrypoints sharing the product's inference code."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import Config, analyze
from .raster import decode_image, serialize


def main() -> None:
    parser = argparse.ArgumentParser(prog="nuclei-lens")
    commands = parser.add_subparsers(dest="command", required=True)
    image = commands.add_parser("analyze", help="Analyze one image locally")
    image.add_argument("image", type=Path)
    image.add_argument("--out", type=Path, required=True)
    benchmark = commands.add_parser("benchmark", help="Evaluate an official dataset partition")
    benchmark.add_argument("--split", choices=["training", "validation", "test"], default="validation")
    benchmark.add_argument("--data", type=Path, default=Path("data/raw/BBBC039"))
    benchmark.add_argument("--out", type=Path, required=True)
    benchmark.add_argument("--limit", type=int)
    benchmark.add_argument("--config", type=Path)
    benchmark.add_argument("--confirm-frozen-protocol", action="store_true")
    args = parser.parse_args()
    if args.command == "analyze":
        result = serialize(analyze(decode_image(args.image.read_bytes())))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result) + "\n")
        print(f"Count {result['raw_count']}; sensitivity {result['sensitivity_range']}; {result['analysis_ms']} ms")
        return
    from .data import Dataset
    from .evaluate import evaluate_partition, save_evaluation
    if args.split == "test" and not (args.confirm_frozen_protocol and args.config):
        parser.error("Test partition is reserved: supply frozen --config and --confirm-frozen-protocol.")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive.")
    config = Config(**json.loads(args.config.read_text())) if args.config else Config()
    with Dataset(args.data) as dataset:
        summary, records = evaluate_partition(dataset, args.split, config, args.limit)
    save_evaluation(summary, records, args.out)
    print(json.dumps({key: summary[key] for key in ["split", "n_images", "count_mae", "mean_f1", "median_analysis_ms"]}, indent=2))


if __name__ == "__main__":
    main()
