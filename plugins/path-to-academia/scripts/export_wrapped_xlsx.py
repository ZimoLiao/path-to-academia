#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from path_to_academia.xlsx import write_xlsx  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a CSV as a wrapped XLSX workbook.")
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("xlsx_path", type=Path)
    args = parser.parse_args()
    write_xlsx(args.csv_path, args.xlsx_path)
    print(args.xlsx_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
