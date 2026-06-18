#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from path_to_academia.quality import run_quality_checks  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run path to academia workspace QA.")
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    report = run_quality_checks(args.workspace)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
