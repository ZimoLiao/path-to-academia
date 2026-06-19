from __future__ import annotations

import csv
import json
from importlib import resources
from pathlib import Path

from . import schemas
from .csvio import write_dicts
from .status import ensure_status_file


def example_resource(*parts: str):
    return resources.files("path_to_academia").joinpath("data", "examples", "ml-bio", *parts)


def read_example_json(*parts: str) -> dict[str, object]:
    return json.loads(example_resource(*parts).read_text(encoding="utf-8"))


def read_example_csv(fields: list[str], *parts: str) -> list[dict[str, str]]:
    with example_resource(*parts).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [{field: row.get(field, "") for field in fields} for row in rows]


def example_config() -> dict[str, object]:
    return read_example_json("configs", "domain.json")


def empty_config() -> dict[str, object]:
    return {
        "project": {
            "name": "path to academia workspace",
            "description": "Configure this workspace through domain terms, evidence rules, and source passes.",
        },
        "domain": {
            "inclusion_terms": [],
            "review_terms": [],
            "exclusion_terms": [],
        },
        "constraints": {
            "opportunity_types": [],
            "geographic_scope": [],
            "age_policy": "Collect only public sourced or clearly estimated age; leave blank when unreliable.",
            "additional_constraints": [],
        },
        "evidence": {
            "named_evidence_filters": [],
            "honor_sources": [],
            "identity_sources": [
                "official profile",
                "Google Scholar author page or search link",
                "ORCID",
                "OpenAlex",
                "Semantic Scholar",
            ],
        },
        "source_passes": [],
        "sentinel_checks": [],
    }


def example_entities() -> list[dict[str, str]]:
    return read_example_csv(schemas.ENTITY_FIELDS, "tables", "entities_final.csv")


def example_sources() -> list[dict[str, str]]:
    return read_example_csv(schemas.SOURCE_FIELDS, "raw", "source_records.csv")


def example_audit_note() -> str:
    return example_resource("audit", "demo_source_note.md").read_text(encoding="utf-8")


def init_workspace(workspace: Path, example: str = "ml-bio", force: bool = False) -> None:
    if example not in {"ml-bio", "empty"}:
        raise ValueError(f"unknown example: {example}")

    workspace = workspace.resolve()
    for dirname in ["configs", "raw", "raw/shards", "tables", "tables/shards", "audit", "ui_state"]:
        (workspace / dirname).mkdir(parents=True, exist_ok=True)

    config_path = workspace / "configs" / "domain.json"
    if force or not config_path.exists():
        config = empty_config() if example == "empty" else example_config()
        config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    entities_path = workspace / "tables" / "entities_final.csv"
    sources_path = workspace / "raw" / "source_records.csv"
    positions_path = workspace / "tables" / "positions_current.csv"
    review_path = workspace / "tables" / "entities_review_or_excluded.csv"

    if example != "empty":
        if force or not entities_path.exists():
            write_dicts(entities_path, schemas.ENTITY_FIELDS, example_entities())
        if force or not sources_path.exists():
            write_dicts(sources_path, schemas.SOURCE_FIELDS, example_sources())
        audit_note = workspace / "audit" / "demo_source_note.md"
        if force or not audit_note.exists():
            audit_note.write_text(example_audit_note(), encoding="utf-8")
    else:
        if force or not entities_path.exists():
            write_dicts(entities_path, schemas.ENTITY_FIELDS, [])
        if force or not sources_path.exists():
            write_dicts(sources_path, schemas.SOURCE_FIELDS, [])

    if force or not positions_path.exists():
        write_dicts(positions_path, schemas.POSITION_FIELDS, [])
    if force or not review_path.exists():
        write_dicts(review_path, schemas.ENTITY_FIELDS, [])
    ensure_status_file(workspace)

    readme = workspace / "README.md"
    if force or not readme.exists():
        readme.write_text(
            "\n".join(
                [
                    "# path to academia Workspace",
                    "",
                    "This workspace separates raw source evidence, final fact tables, audit reports, and private outreach state.",
                    "",
                    "- `raw/`: source records and intermediate evidence",
                    "- `raw/shards/`: per-source or per-worker extraction batches",
                    "- `tables/`: final and review CSV outputs",
                    "- `tables/shards/`: per-worker candidate, review, or position outputs before merge",
                    "- `audit/`: quality reports and source notes",
                    "- `ui_state/`: private outreach status sidecar",
                    "",
                ]
            ),
            encoding="utf-8",
        )
