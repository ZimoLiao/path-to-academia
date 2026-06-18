#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from path_to_academia.workspace import init_workspace  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a path to academia workspace.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--example", default="ml-bio", choices=["ml-bio", "empty"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    init_workspace(args.workspace, example=args.example, force=args.force)
    print(args.workspace.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
