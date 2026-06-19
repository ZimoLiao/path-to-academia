from __future__ import annotations

import json
from pathlib import Path

from .quality import build_quality_report


def read_domain_config(workspace: Path) -> dict[str, object]:
    config_path = workspace / "configs" / "domain.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def list_values(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def named_filter_names(filters: list[object]) -> list[str]:
    names: list[str] = []
    for item in filters:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            names.append(name)
    return names


def build_workspace_context(workspace: Path) -> dict[str, object]:
    workspace = workspace.resolve()
    config = read_domain_config(workspace)
    project = config.get("project", {}) if isinstance(config.get("project", {}), dict) else {}
    domain = config.get("domain", {}) if isinstance(config.get("domain", {}), dict) else {}
    constraints = config.get("constraints", {}) if isinstance(config.get("constraints", {}), dict) else {}
    evidence = config.get("evidence", {}) if isinstance(config.get("evidence", {}), dict) else {}
    named_filters = list_values(evidence.get("named_evidence_filters", []))
    named_filter_name_list = named_filter_names(named_filters)
    legacy_exact = list_values(evidence.get("target_venues", []))
    legacy_related = list_values(evidence.get("related_venue_families", []))
    source_passes = list_values(config.get("source_passes", []))
    evidence_context: dict[str, object] = {
        "named_evidence_filters": named_filters,
        "named_evidence_filter_names": named_filter_name_list,
        "honor_sources": list_values(evidence.get("honor_sources", [])),
        "identity_sources": list_values(evidence.get("identity_sources", [])),
    }
    if legacy_exact:
        evidence_context["legacy_exact_evidence_names"] = legacy_exact
    if legacy_related:
        evidence_context["legacy_related_evidence_groups"] = legacy_related

    return {
        "workspace": str(workspace),
        "project": {
            "name": project.get("name", ""),
            "description": project.get("description", ""),
        },
        "domain": {
            "inclusion_terms": list_values(domain.get("inclusion_terms", [])),
            "review_terms": list_values(domain.get("review_terms", [])),
            "exclusion_terms": list_values(domain.get("exclusion_terms", [])),
        },
        "constraints": {
            "opportunity_types": list_values(constraints.get("opportunity_types", [])),
            "geographic_scope": list_values(constraints.get("geographic_scope", [])),
            "age_policy": constraints.get("age_policy", ""),
            "additional_constraints": list_values(constraints.get("additional_constraints", [])),
        },
        "evidence": evidence_context,
        "terminology": {
            "named_evidence_filters": "user-owned concrete evidence labels",
            "named_evidence_filter_names": "configured concrete evidence labels by name",
            "evidence_items": "concrete filterable evidence labels found for an entity",
            "evidence_summary": "short explanation of matched evidence labels",
            "age": "publicly sourced or transparent estimated age",
            "age_evidence": "source or caveat for age collection",
        },
        "source_passes": source_passes,
        "quality": build_quality_report(workspace),
        "files": {
            "domain_config": "configs/domain.json",
            "raw_sources": "raw/source_records.csv",
            "final_entities": "tables/entities_final.csv",
            "review_entities": "tables/entities_review_or_excluded.csv",
            "current_positions": "tables/positions_current.csv",
            "private_status": "ui_state/outreach_status.csv",
            "quality_report": "audit/quality_report.json",
        },
        "privacy_boundary": {
            "public_facts": ["tables/entities_final.csv", "tables/entities_review_or_excluded.csv", "tables/positions_current.csv"],
            "private_state": "ui_state/outreach_status.csv",
            "rule": "Do not write priority, contact state, dates, next actions, or private notes into public fact tables.",
        },
        "agent_next_steps": [
            "Review configs/domain.json before collecting sources.",
            "Run path-to-academia qa after table edits.",
            "Preserve source URLs and audit notes for manual judgments.",
            "Treat blank enrichment as unknown or not collected, not negative evidence.",
            "Keep named evidence filters, honor sources, age policy, and other constraints user-owned; ask before auto-filling broad lists.",
            "Collect Google Scholar author-page links when available; otherwise use a clearly labeled search link or audit why Scholar was not collected.",
            "Collect age only from public sourced facts or transparent estimates, and leave it blank when unreliable.",
        ],
    }
