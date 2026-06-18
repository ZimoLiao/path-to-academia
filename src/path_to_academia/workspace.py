from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import schemas
from .csvio import write_dicts
from .status import ensure_status_file


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def example_config() -> dict[str, object]:
    return {
        "project": {
            "name": "ML and Biology Starter Workspace",
            "description": "Synthetic starter workspace for research groups and open roles.",
        },
        "domain": {
            "inclusion_terms": [
                "machine learning",
                "representation learning",
                "computational biology",
                "genomics",
                "biomedical AI",
                "clinical translation",
            ],
            "review_terms": ["adjacent methods", "platform team", "infrastructure"],
            "exclusion_terms": ["student-only", "expired", "unverified identity"],
        },
        "evidence": {
            "target_venues": ["Nature", "Science", "Cell", "NeurIPS", "ICML", "ICLR"],
            "identity_sources": ["official profile", "ORCID", "OpenAlex", "Semantic Scholar"],
        },
        "source_passes": [
            {"name": "official group pages", "type": "profile_source"},
            {"name": "conference award and keynote lists", "type": "reverse_discovery"},
            {"name": "open position boards", "type": "position_source"},
        ],
    }


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
        "evidence": {
            "target_venues": [],
            "identity_sources": ["official profile", "ORCID", "OpenAlex", "Semantic Scholar"],
        },
        "source_passes": [],
    }


def example_entities() -> list[dict[str, str]]:
    retrieved_at = now_iso()
    return [
        {
            "retrieved_at": retrieved_at,
            "source_batch": "synthetic_example",
            "source_name": "Example Institute AI Lab",
            "source_url": "https://example.org/ai-lab",
            "all_source_urls": "https://example.org/ai-lab",
            "all_source_names": "Example Institute AI Lab",
            "name": "Ada Kim",
            "role_title": "Associate Professor",
            "institution": "Example Institute",
            "department_or_group": "AI Lab",
            "country": "United States",
            "summary_text": "Representation learning, robust evaluation, and trustworthy model behavior.",
            "domain_tags": "machine learning; representation learning",
            "homepage_url": "https://example.org/people/ada-kim",
            "orcid_url": "",
            "scholar_url": "",
            "openalex_url": "",
            "semantic_scholar_url": "",
            "h_index": "42",
            "citation_count": "12000",
            "metric_source": "synthetic example",
            "honors": "Example early career award",
            "target_venue_exact": "yes",
            "target_venue_family": "yes",
            "target_publication_evidence": "Synthetic NeurIPS and Nature Machine Intelligence evidence.",
            "relevance_status": "include",
            "relevance_reason": "domain_terms_in_profile",
            "relevance_evidence": "Official example profile describes representation learning and robust evaluation.",
            "notes": "Synthetic row for product demonstration.",
        },
        {
            "retrieved_at": retrieved_at,
            "source_batch": "synthetic_example",
            "source_name": "Example Genome Center",
            "source_url": "https://example.org/genome-center",
            "all_source_urls": "https://example.org/genome-center",
            "all_source_names": "Example Genome Center",
            "name": "Mateo Silva",
            "role_title": "Group Leader",
            "institution": "Example Genome Center",
            "department_or_group": "Computational Genomics",
            "country": "Spain",
            "summary_text": "Sequence models, single-cell analysis, and interpretable genomics.",
            "domain_tags": "computational biology; genomics",
            "homepage_url": "https://example.org/people/mateo-silva",
            "orcid_url": "",
            "scholar_url": "",
            "openalex_url": "",
            "semantic_scholar_url": "",
            "h_index": "35",
            "citation_count": "8400",
            "metric_source": "synthetic example",
            "honors": "",
            "target_venue_exact": "no",
            "target_venue_family": "yes",
            "target_publication_evidence": "Synthetic Cell Systems evidence.",
            "relevance_status": "include",
            "relevance_reason": "domain_terms_in_profile",
            "relevance_evidence": "Official example profile describes computational genomics and sequence models.",
            "notes": "Synthetic row for product demonstration.",
        },
        {
            "retrieved_at": retrieved_at,
            "source_batch": "synthetic_example",
            "source_name": "Example Medical AI Program",
            "source_url": "https://example.org/medical-ai",
            "all_source_urls": "https://example.org/medical-ai",
            "all_source_names": "Example Medical AI Program",
            "name": "Priya Nair",
            "role_title": "Principal Investigator",
            "institution": "Example Medical School",
            "department_or_group": "Biomedical AI",
            "country": "India",
            "summary_text": "Clinical decision support, multimodal learning, and deployment evaluation.",
            "domain_tags": "biomedical AI; clinical translation",
            "homepage_url": "https://example.org/people/priya-nair",
            "orcid_url": "",
            "scholar_url": "",
            "openalex_url": "",
            "semantic_scholar_url": "",
            "h_index": "29",
            "citation_count": "5100",
            "metric_source": "synthetic example",
            "honors": "Example translational research prize",
            "target_venue_exact": "no",
            "target_venue_family": "yes",
            "target_publication_evidence": "Synthetic medical AI venue evidence.",
            "relevance_status": "include",
            "relevance_reason": "domain_terms_in_profile",
            "relevance_evidence": "Official example profile describes biomedical AI and clinical translation.",
            "notes": "Synthetic row for product demonstration.",
        },
    ]


def example_sources() -> list[dict[str, str]]:
    rows = []
    for row in example_entities():
        rows.append(
            {
                "retrieved_at": row["retrieved_at"],
                "source_batch": row["source_batch"],
                "source_name": row["source_name"],
                "source_url": row["source_url"],
                "source_type": "synthetic_profile_page",
                "record_type": "person",
                "name": row["name"],
                "role_title": row["role_title"],
                "institution": row["institution"],
                "department_or_group": row["department_or_group"],
                "country": row["country"],
                "summary_text": row["summary_text"],
                "keyword_hits": row["domain_tags"],
                "homepage_url": row["homepage_url"],
                "orcid_url": row["orcid_url"],
                "scholar_url": row["scholar_url"],
                "metric_h_index": row["h_index"],
                "metric_source": row["metric_source"],
                "citation_count": row["citation_count"],
                "honors": row["honors"],
                "raw_text": row["summary_text"],
                "extraction_method": "synthetic seed",
                "notes": row["notes"],
            }
        )
    return rows


def init_workspace(workspace: Path, example: str = "ml-bio", force: bool = False) -> None:
    if example not in {"ml-bio", "empty"}:
        raise ValueError(f"unknown example: {example}")

    workspace = workspace.resolve()
    for dirname in ["configs", "raw", "tables", "audit", "ui_state"]:
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
                    "- `tables/`: final and review CSV outputs",
                    "- `audit/`: quality reports and source notes",
                    "- `ui_state/`: private outreach status sidecar",
                    "",
                ]
            ),
            encoding="utf-8",
        )
