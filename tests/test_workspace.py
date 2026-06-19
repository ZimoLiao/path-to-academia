from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from path_to_academia import schemas
from path_to_academia.context import build_workspace_context
from path_to_academia.quality import person_key, run_quality_checks
from path_to_academia.status import upsert_status
from path_to_academia.workspace import example_config, init_workspace


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_init_workspace_creates_generic_ml_bio_example(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"

    init_workspace(workspace, example="ml-bio")

    expected_dirs = ["configs", "raw", "raw/shards", "tables", "tables/shards", "audit", "ui_state"]
    for dirname in expected_dirs:
        assert (workspace / dirname).is_dir()

    config = json.loads((workspace / "configs" / "domain.json").read_text(encoding="utf-8"))
    assert config["project"]["name"] == "ML and Biology Starter Workspace"
    assert "inclusion_terms" in config["domain"]
    assert "named_evidence_filters" in config["evidence"]
    assert "honor_sources" in config["evidence"]
    assert "age_policy" in config["constraints"]
    assert "additional_constraints" in config["constraints"]
    assert "sentinel_checks" in config

    entities = read_rows(workspace / "tables" / "entities_final.csv")
    assert len(entities) == 3
    assert list(entities[0].keys()) == schemas.ENTITY_FIELDS
    assert entities[0]["evidence_items"] == "Nature Machine Intelligence; NeurIPS; Example Academy Fellowship; Example Early Career Medal"
    assert entities[0]["age_as_of"] == entities[0]["retrieved_at"].split("T", 1)[0]
    assert int(entities[0]["age"]) == int(entities[0]["age_as_of"][:4]) - int(entities[0]["birth_year"])
    assert "synthetic" in entities[0]["age_evidence"].lower()
    assert {row["domain_tags"] for row in entities} == {
        "machine learning; representation learning",
        "computational biology; genomics",
        "biomedical AI; clinical translation",
    }

    sources = read_rows(workspace / "raw" / "source_records.csv")
    assert len(sources) == 3
    assert list(sources[0].keys()) == schemas.SOURCE_FIELDS


def test_init_workspace_empty_example_has_blank_config_and_tables(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"

    init_workspace(workspace, example="empty")

    config = json.loads((workspace / "configs" / "domain.json").read_text(encoding="utf-8"))
    assert config["domain"]["inclusion_terms"] == []
    assert config["evidence"]["named_evidence_filters"] == []
    assert config["evidence"]["honor_sources"] == []
    assert config["constraints"]["age_policy"] == "Collect only public sourced or clearly estimated age; leave blank when unreliable."
    assert config["constraints"]["additional_constraints"] == []
    assert config["sentinel_checks"] == []
    assert read_rows(workspace / "tables" / "entities_final.csv") == []
    assert read_rows(workspace / "raw" / "source_records.csv") == []


def test_checked_in_ml_bio_example_config_matches_generated_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    checked_in = json.loads((root / "examples" / "ml-bio" / "configs" / "domain.json").read_text(encoding="utf-8"))
    generated = example_config()

    assert checked_in["constraints"] == generated["constraints"]
    assert checked_in["evidence"] == generated["evidence"]


def test_context_preserves_legacy_evidence_config_keys(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    init_workspace(workspace, example="empty")
    config_path = workspace / "configs" / "domain.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["evidence"]["target_venues"] = ["Nature", "Science"]
    config["evidence"]["related_venue_families"] = ["Nature Portfolio"]
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    context = build_workspace_context(workspace)

    assert context["evidence"]["target_venues"] == ["Nature", "Science"]
    assert context["evidence"]["related_venue_families"] == ["Nature Portfolio"]
    assert context["evidence"]["legacy_exact_evidence_names"] == ["Nature", "Science"]
    assert context["evidence"]["legacy_related_evidence_groups"] == ["Nature Portfolio"]


def test_init_workspace_rejects_unknown_example(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown example"):
        init_workspace(tmp_path / "workspace", example="unknown")


def test_status_sidecar_does_not_modify_fact_table(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    init_workspace(workspace, example="ml-bio")
    fact_table = workspace / "tables" / "entities_final.csv"
    before = sha256(fact_table)

    row = read_rows(fact_table)[0]
    updated = upsert_status(
        workspace,
        {
            "person_key": person_key(row["name"], row["institution"]),
            "name": row["name"],
            "institution": row["institution"],
            "status": "to_apply",
            "priority": "high",
            "private_note": "Synthetic test note",
        },
    )

    after = sha256(fact_table)
    assert before == after
    assert updated["status"] == "to_apply"
    status_rows = read_rows(workspace / "ui_state" / "outreach_status.csv")
    assert len(status_rows) == 1
    assert status_rows[0]["person_key"] == person_key(row["name"], row["institution"])


def test_status_upsert_rejects_blank_identity(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    init_workspace(workspace, example="ml-bio")

    with pytest.raises(ValueError, match="person_key or name and institution"):
        upsert_status(workspace, {"name": "", "institution": ""})


def test_status_upsert_preserves_unspecified_existing_fields(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    init_workspace(workspace, example="ml-bio")
    row = read_rows(workspace / "tables" / "entities_final.csv")[0]
    key = person_key(row["name"], row["institution"])

    upsert_status(
        workspace,
        {
            "person_key": key,
            "name": row["name"],
            "institution": row["institution"],
            "status": "to_apply",
            "private_note": "Keep this note",
        },
    )
    updated = upsert_status(workspace, {"person_key": key, "status": "rejected"})

    assert updated["name"] == row["name"]
    assert updated["institution"] == row["institution"]
    assert updated["private_note"] == "Keep this note"
    assert updated["status"] == "rejected"


def test_quality_checks_find_blank_fields_and_duplicates(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    init_workspace(workspace, example="ml-bio")
    fact_table = workspace / "tables" / "entities_final.csv"
    rows = read_rows(fact_table)
    rows.append(dict(rows[0]))
    rows[-1]["summary_text"] = ""
    with fact_table.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=schemas.ENTITY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    report = run_quality_checks(workspace)

    assert report["row_count"] == 4
    assert report["duplicate_person_keys"] == 1
    assert "summary_text" in report["blank_required_fields"]
    assert report["enrichment_coverage"]["scholar_url"] == 0
    assert report["enrichment_coverage"]["honors"] == 3
    assert report["enrichment_coverage"]["evidence_items"] == 4
    assert report["enrichment_coverage"]["evidence_summary"] == 4
    assert report["enrichment_coverage"]["age"] == 4
    assert report["enrichment_coverage"]["age_evidence"] == 4
    assert report["unmatched_status_count"] == 0


def test_schema_fields_have_semantic_descriptions() -> None:
    missing = sorted(schemas.all_schema_fields() - set(schemas.FIELD_DESCRIPTIONS))
    extra = sorted(set(schemas.FIELD_DESCRIPTIONS) - schemas.all_schema_fields())
    assert missing == []
    assert extra == []
