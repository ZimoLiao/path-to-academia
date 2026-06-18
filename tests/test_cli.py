from __future__ import annotations

import json
from pathlib import Path

from path_to_academia.cli import main


def test_cli_initializes_checks_and_exports_workspace(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"
    xlsx_path = workspace / "tables" / "entities_final_wrapped.xlsx"

    assert main(["init", str(workspace), "--example", "ml-bio"]) == 0
    capsys.readouterr()
    assert (workspace / "configs" / "domain.json").exists()

    assert main(["qa", str(workspace)]) == 0
    qa_output = json.loads(capsys.readouterr().out)
    assert qa_output["row_count"] == 3
    assert qa_output["duplicate_person_keys"] == 0

    assert main(["context", str(workspace)]) == 0
    context_output = json.loads(capsys.readouterr().out)
    assert context_output["project"]["name"] == "ML and Biology Starter Workspace"
    assert context_output["quality"]["row_count"] == 3
    assert context_output["evidence"]["related_venue_families"]
    assert context_output["evidence"]["honor_sources"]
    assert "Google Scholar author page" in context_output["evidence"]["identity_sources"]
    assert "additional_constraints" in context_output["constraints"]
    assert context_output["privacy_boundary"]["private_state"] == "ui_state/outreach_status.csv"

    assert main(["export-xlsx", str(workspace / "tables" / "entities_final.csv"), str(xlsx_path)]) == 0
    assert xlsx_path.exists()
