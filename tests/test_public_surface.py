from __future__ import annotations

import re
from pathlib import Path


def banned_domain_terms() -> set[str]:
    return {
        "fl" + "uid",
        "tur" + "bulence",
        "particle" + "-laden",
        "geo" + "physical",
        "astro" + "physical",
        "sedi" + "ment",
        "cloud " + "microphysics",
    }


def test_public_product_has_no_private_domain_residue() -> None:
    root = Path(__file__).resolve().parents[1]
    checked_suffixes = {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".html", ".css", ".js"}
    offenders: list[str] = []
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix not in checked_suffixes:
            continue
        if ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for term in banned_domain_terms():
            if term in text:
                offenders.append(f"{path.relative_to(root)}:{term}")
    assert offenders == []


def test_skill_markdown_references_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    skill_path = root / "skills" / "path-to-academia" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    referenced = {
        match.group(1)
        for match in re.finditer(r"`([^`]+[.]md)`", text)
        if match.group(1).startswith(("../", "docs/", "references/"))
    }

    missing = []
    for raw_path in referenced:
        target = (skill_path.parent / raw_path).resolve()
        if not target.exists():
            missing.append(raw_path)
    assert missing == []


def test_skill_includes_constraint_driven_search_guidance() -> None:
    root = Path(__file__).resolve().parents[1]
    skill_path = root / "skills" / "path-to-academia" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8").lower()

    required_terms = [
        "constraint-driven search",
        "journal",
        "conference",
        "award",
        "funder",
        "job board",
        "institution",
    ]

    missing = [term for term in required_terms if term not in text]
    assert missing == []


def test_skill_requires_incremental_persistence_during_collection() -> None:
    root = Path(__file__).resolve().parents[1]
    skill_path = root / "skills" / "path-to-academia" / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8").lower()

    required_terms = [
        "incremental persistence",
        "do not browse",
        "context",
        "write rows",
        "before continuing",
        "subagent",
    ]

    missing = [term for term in required_terms if term not in text]
    assert missing == []


def test_collection_playbook_deposits_large_collection_lessons() -> None:
    root = Path(__file__).resolve().parents[1]
    playbook_path = root / "docs" / "collection-playbook.md"
    text = playbook_path.read_text(encoding="utf-8").lower()

    required_terms = [
        "seed roster",
        "sentinel",
        "source-batch",
        "extraction",
        "ranking",
        "reverse-discovery",
        "fixed schema",
        "rate limits",
        "name-only",
        "resume",
    ]

    missing = [term for term in required_terms if term not in text]
    assert missing == []
