from __future__ import annotations

import zipfile
import csv
from pathlib import Path
from xml.etree import ElementTree

from path_to_academia.workspace import init_workspace
from path_to_academia.xlsx import write_xlsx


def worksheet_row_count(path: Path) -> int:
    with zipfile.ZipFile(path) as archive:
        data = archive.read("xl/worksheets/sheet1.xml")
    root = ElementTree.fromstring(data)
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    return len(root.findall(".//x:sheetData/x:row", ns))


def test_write_xlsx_preserves_csv_rows(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    init_workspace(workspace, example="ml-bio")
    csv_path = workspace / "tables" / "entities_final.csv"
    xlsx_path = workspace / "tables" / "entities_final_wrapped.xlsx"

    write_xlsx(csv_path, xlsx_path)

    assert xlsx_path.exists()
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        expected_rows = len(list(csv.DictReader(handle))) + 1
    assert worksheet_row_count(xlsx_path) == expected_rows
