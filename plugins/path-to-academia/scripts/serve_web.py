#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from path_to_academia.web import serve  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the path to academia local web UI.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(args.workspace, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
