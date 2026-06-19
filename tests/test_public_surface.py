from __future__ import annotations

import re
from pathlib import Path


PUBLIC_TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".html", ".css", ".js", ".cff"}


def public_text_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir() or path.suffix not in PUBLIC_TEXT_SUFFIXES:
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in {".git", ".pytest_cache", "__pycache__", "build"} for part in relative_parts):
            continue
        if relative_parts[0] == "tests":
            continue
        paths.append(path)
    return paths


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


def test_readme_current_release_matches_project_version() -> None:
    root = Path(__file__).resolve().parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")

    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, flags=re.MULTILINE)
    readme_match = re.search(r"Current release:\s*`([^`]+)`", readme)

    assert version_match is not None
    assert readme_match is not None
    assert readme_match.group(1) == version_match.group(1)


def test_readme_opens_with_plain_product_purpose() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    plugin_readme = (root / "plugins" / "path-to-academia" / "README.md").read_text(encoding="utf-8")
    first_paragraph = readme.split("\n\n", 2)[1].lower()
    plugin_first_paragraph = plugin_readme.split("\n\n", 2)[1].lower()

    for text in [first_paragraph, plugin_first_paragraph]:
        assert "plugin" in text
        assert "claude code" in text
        assert "codex" in text
        assert "phd" in text
        assert "postdoc" in text
        assert "supervisors" in text
        assert "positions" in text


def test_release_metadata_versions_match_project_version() -> None:
    root = Path(__file__).resolve().parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, flags=re.MULTILINE)
    assert version_match is not None
    version = version_match.group(1)

    version_sources = {
        "src/path_to_academia/__init__.py": r'__version__\s*=\s*"([^"]+)"',
        "plugins/path-to-academia/src/path_to_academia/__init__.py": r'__version__\s*=\s*"([^"]+)"',
        "CITATION.cff": r'^version:\s*"([^"]+)"',
        "plugins/path-to-academia/CITATION.cff": r'^version:\s*"([^"]+)"',
        "plugins/path-to-academia/pyproject.toml": r'^version\s*=\s*"([^"]+)"',
    }

    mismatches: list[str] = []
    for relative_path, pattern in version_sources.items():
        text = (root / relative_path).read_text(encoding="utf-8")
        match = re.search(pattern, text, flags=re.MULTILINE)
        if not match:
            mismatches.append(f"{relative_path}:missing")
        elif match.group(1) != version:
            mismatches.append(f"{relative_path}:{match.group(1)}")

    assert mismatches == []


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


def test_guided_intake_requires_separate_evidence_questions() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8").lower()
    skill = (root / "skills" / "path-to-academia" / "SKILL.md").read_text(encoding="utf-8").lower()
    manifest = (root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8").lower()
    surface = readme + "\n" + skill + "\n" + manifest

    required_terms = [
        "ask these as separate questions",
        "named evidence filters",
        "concrete evidence items",
        "honor sources",
        "other constraints",
        "age",
        "do not auto-fill",
        "google scholar",
    ]

    missing = [term for term in required_terms if term not in surface]
    assert missing == []


def test_public_guidance_uses_clear_journal_conference_terms() -> None:
    root = Path(__file__).resolve().parents[1]
    banned_phrases = [
        "target venues",
        "target venue",
        "target journals/conferences",
        "target journal/conference",
        "target journals",
        "target journal",
        "related venue families",
        "related venue family",
        "related journal/conference families",
        "related journal/conference family",
        "publication venue",
        "publication venues",
        "venue evidence",
        "venue constraints",
        "venue sweeps",
        "venue family",
        "venue families",
        "venue/award",
        "venue-family",
        "target-venue",
        "evidence venues",
        "publication signal",
        "publication signals",
        "synthetic medical ai venue evidence",
    ]
    offenders: list[str] = []
    for path in public_text_paths(root):
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in banned_phrases:
            if phrase in text:
                offenders.append(f"{path.relative_to(root)}:{phrase}")

    assert offenders == []


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
