#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from path_to_academia.context import build_workspace_context  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Print agent-ready path to academia workspace context.")
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_workspace_context(args.workspace), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

