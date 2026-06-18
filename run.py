#!/usr/bin/env python3
"""
run.py
-------
CLI entry point for the Intelligent Candidate Discovery pipeline.

Usage:
    python run.py                      # uses config.yaml as-is
    python run.py --config my.yaml     # use an alternate config file

The pipeline reads everything it needs from config.yaml (data paths,
column mappings, ranking weights, top_k, optional LLM re-ranking) so this
file stays tiny and stable.
"""

import argparse
import yaml

from src.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Intelligent Candidate Discovery pipeline")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML file")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    run_pipeline(config)


if __name__ == "__main__":
    main()
