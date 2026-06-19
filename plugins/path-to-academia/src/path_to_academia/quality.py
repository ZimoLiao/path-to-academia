from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from . import schemas
from .csvio import read_dicts, write_dicts


def normalize_key(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode()
    folded = re.sub(r"[^a-z0-9]+", "-", folded.lower())
    return folded.strip("-")


def person_key(name: str, institution: str) -> str:
    return f"{normalize_key(name)}__{normalize_key(institution)}"


def build_quality_report(workspace: Path) -> dict[str, object]:
    table = workspace / "tables" / "entities_final.csv"
    status_file = workspace / "ui_state" / "outreach_status.csv"
    _, rows = read_dicts(table)
    _, statuses = read_dicts(status_file)

    blank_required: dict[str, int] = {}
    for field in schemas.REQUIRED_ENTITY_FIELDS:
        count = sum(1 for row in rows if not row.get(field, "").strip())
        if count:
            blank_required[field] = count

    keys = [person_key(row.get("name", ""), row.get("institution", "")) for row in rows]
    duplicate_person_keys = sum(1 for _, count in Counter(keys).items() if count > 1)
    known = set(keys)
    unmatched = [row for row in statuses if row.get("person_key", "") not in known]
    enrichment_fields = [
        "homepage_url",
        "orcid_url",
        "scholar_url",
        "openalex_url",
        "semantic_scholar_url",
        "honors",
        "evidence_items",
        "evidence_summary",
        "target_publication_evidence",
        "age",
        "age_evidence",
    ]
    enrichment_coverage = {
        field: sum(1 for row in rows if row.get(field, "").strip()) for field in enrichment_fields
    }

    report: dict[str, object] = {
        "row_count": len(rows),
        "status_count": len(statuses),
        "duplicate_person_keys": duplicate_person_keys,
        "blank_required_fields": blank_required,
        "unmatched_status_count": len(unmatched),
        "unmatched_status_keys": [row.get("person_key", "") for row in unmatched],
        "enrichment_coverage": enrichment_coverage,
        "fact_table": str(table),
        "status_file": str(status_file),
    }
    return report


def run_quality_checks(workspace: Path) -> dict[str, object]:
    report = build_quality_report(workspace)
    audit = workspace / "audit" / "quality_report.json"
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def rebuild_status_keys(workspace: Path) -> None:
    fields, rows = read_dicts(workspace / "ui_state" / "outreach_status.csv")
    if not fields:
        fields = schemas.STATUS_FIELDS
    for row in rows:
        row["person_key"] = row.get("person_key") or person_key(row.get("name", ""), row.get("institution", ""))
    write_dicts(workspace / "ui_state" / "outreach_status.csv", fields, rows)
