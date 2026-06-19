from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from path_to_academia.web import WorkspaceHandler, make_handler
from path_to_academia.workspace import init_workspace


def get_json(url: str) -> dict[str, object]:
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def test_web_api_serves_workspace_records_and_status(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    init_workspace(workspace, example="ml-bio")
    handler: type[WorkspaceHandler] = make_handler(workspace)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        health = get_json(f"{base}/api/health")
        records = get_json(f"{base}/api/entities")
        statuses = get_json(f"{base}/api/status")
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert health["status"] == "ok"
    assert health["entity_count"] == 3
    assert records["count"] == 3
    assert records["source"] == "tables/entities_final.csv"
    assert statuses["count"] == 0


def test_static_ui_exposes_core_workspace_controls() -> None:
    root = Path(__file__).resolve().parents[1]
    html = (root / "src" / "path_to_academia" / "webui" / "static" / "index.html").read_text(encoding="utf-8")
    js = (root / "src" / "path_to_academia" / "webui" / "static" / "app.js").read_text(encoding="utf-8")
    i18n = (root / "src" / "path_to_academia" / "webui" / "static" / "i18n.json").read_text(encoding="utf-8")
    surface = html + "\n" + js + "\n" + i18n

    required_controls = [
        "topStats",
        "tagTree",
        "statusFilters",
        "minH",
        "minCites",
        "last_contacted",
        "next_action_date",
        "dossier.sourceProvenance",
    ]
    for control in required_controls:
        assert control in surface


def test_static_ui_makes_profile_links_and_evidence_badges_actionable() -> None:
    root = Path(__file__).resolve().parents[1]
    js = (root / "src" / "path_to_academia" / "webui" / "static" / "app.js").read_text(encoding="utf-8")
    css = (root / "src" / "path_to_academia" / "webui" / "static" / "styles.css").read_text(encoding="utf-8")
    surface = js + "\n" + css

    required_fragments = [
        "function renderCardActions(row)",
        "card-actions",
        "link.homepage",
        'data-evidence-section="${escapeAttr(sectionName)}"',
        'evidenceBadge(row, "honors"',
        'evidenceBadge(row, "targetPublication"',
        "function focusDossierSection",
        'event.target.closest("a, button',
        "function linkifyText",
        "sourceSection(row)",
        'target="_blank"',
        'rel="noreferrer"',
    ]
    for fragment in required_fragments:
        assert fragment in surface


def test_static_ui_has_complete_localization_boundary() -> None:
    root = Path(__file__).resolve().parents[1]
    html = (root / "src" / "path_to_academia" / "webui" / "static" / "index.html").read_text(encoding="utf-8")
    js = (root / "src" / "path_to_academia" / "webui" / "static" / "app.js").read_text(encoding="utf-8")
    i18n = json.loads((root / "src" / "path_to_academia" / "webui" / "static" / "i18n.json").read_text(encoding="utf-8"))

    expected_languages = {"en", "zh-CN", "zh-TW", "ja", "ko", "fr", "de", "es", "pt-BR"}
    assert expected_languages.issubset(i18n)
    english_keys = set(i18n["en"])
    assert "label.priority" in english_keys
    assert "label.lastContacted" in english_keys
    assert "label.nextAction" in english_keys
    assert "status.waiting_reply" in english_keys
    for language, translations in i18n.items():
        assert set(translations) == english_keys, language
        assert all(isinstance(value, str) and value for value in translations.values())

    assert 'id="languageSelect"' in html
    assert 'data-i18n="filters.title"' in html
    assert "loadTranslations" in js
    assert "localStorage" in js
    assert "document.documentElement.lang" in js
    assert "status: draftStatus" in js
    assert "escapeHtml(row.name)" in js
    assert "escapeHtml(row.institution)" in js


def test_topbar_language_selector_and_copy_are_compact() -> None:
    root = Path(__file__).resolve().parents[1]
    html = (root / "src" / "path_to_academia" / "webui" / "static" / "index.html").read_text(encoding="utf-8")
    css = (root / "src" / "path_to_academia" / "webui" / "static" / "styles.css").read_text(encoding="utf-8")
    i18n = json.loads((root / "src" / "path_to_academia" / "webui" / "static" / "i18n.json").read_text(encoding="utf-8"))

    assert "<label class=\"language-control\">" not in html
    assert 'id="languageSelect"' in html
    assert 'class="language-control"' in html
    assert 'aria-label="Language"' in html
    assert "height: 24px" in css
    assert ".language-control {" in css

    forbidden_fragments = [
        "Agent-native",
        "Agent native",
        "Agent 原生",
        "证据" + "档案",
        "證據" + "檔案",
        "Evidence " + "Dossier",
        "Evidenz" + "dossier",
        "証拠" + "ドシエ",
        "Dossier de " + "preuves",
        "Dossier de " + "evidencia",
        "Dossiê de " + "evidências",
    ]
    serialized = json.dumps(i18n, ensure_ascii=False) + html
    for fragment in forbidden_fragments:
        assert fragment not in serialized

    assert i18n["en"]["dossier.title"] == "Profile"
    assert i18n["zh-CN"]["dossier.title"] == "档案"
    assert i18n["ja"]["dossier.title"] == "詳細"


def test_language_selector_stays_aligned_with_stats_for_long_locales() -> None:
    root = Path(__file__).resolve().parents[1]
    css = (root / "src" / "path_to_academia" / "webui" / "static" / "styles.css").read_text(encoding="utf-8")
    i18n = json.loads((root / "src" / "path_to_academia" / "webui" / "static" / "i18n.json").read_text(encoding="utf-8"))

    topbar_right = css[css.index(".topbar__right {") : css.index("}", css.index(".topbar__right {"))]
    stats_block = css[css.index(".topbar__stats {") : css.index("}", css.index(".topbar__stats {"))]
    language_block = css[css.index(".language-control {") : css.index("}", css.index(".language-control {"))]

    assert "display: grid" in topbar_right
    assert "grid-template-columns: auto minmax(0, 1fr)" in topbar_right
    assert "align-items: center" in topbar_right
    assert "min-width: 0" in stats_block
    assert "flex-wrap: wrap" in stats_block
    assert "height: 24px" in language_block
    assert "min-height: 24px" in language_block
    assert i18n["de"]["top.records"]
    assert i18n["es"]["top.records"]


def test_public_brand_is_path_to_academia_without_subtitle() -> None:
    root = Path(__file__).resolve().parents[1]
    html = (root / "src" / "path_to_academia" / "webui" / "static" / "index.html").read_text(encoding="utf-8")
    i18n_text = (root / "src" / "path_to_academia" / "webui" / "static" / "i18n.json").read_text(encoding="utf-8")
    manifest = (root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    surface = html + "\n" + i18n_text + "\n" + manifest

    assert "<h1>path to academia</h1>" in html
    assert "Academic Opportunity " + "Atlas" not in surface
    assert "Research " + "workspace" not in surface
    assert "研究" + "工作台" not in surface
    assert "app." + "eyebrow" not in surface


def test_plugin_docs_start_with_guided_agent_intake() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    skill = (root / "skills" / "path-to-academia" / "SKILL.md").read_text(encoding="utf-8")
    manifest = json.loads((root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    surface = readme + "\n" + skill + "\n" + "\n".join(manifest["interface"]["defaultPrompt"])

    required_guidance = [
        "Guided Intake",
        "research direction",
        "constraints",
        "geographic scope",
        "target journals/conferences",
        "related journal/conference families",
        "honor sources",
        "Google Scholar",
        "output format",
        "Do not start source collection",
    ]
    for phrase in required_guidance:
        assert phrase in surface


def test_static_ui_uses_clear_journal_conference_labels() -> None:
    root = Path(__file__).resolve().parents[1]
    i18n = json.loads((root / "src" / "path_to_academia" / "webui" / "static" / "i18n.json").read_text(encoding="utf-8"))

    assert i18n["en"]["filters.targetJournalConference"] == "Target journal/conference"
    assert i18n["en"]["filters.relatedJournalConference"] == "Related journal/conference family"
    assert i18n["en"]["sort.journalConference"] == "Journal/conference evidence"
    assert i18n["en"]["badge.targetJournalConference"] == "Target journal/conference"
    assert i18n["en"]["badge.relatedJournalConference"] == "Related journal/conference"
    assert i18n["en"]["dossier.targetPublication"] == "Target journal/conference evidence"
    assert i18n["zh-CN"]["filters.targetJournalConference"] == "重点期刊/会议"
    assert i18n["zh-CN"]["filters.relatedJournalConference"] == "相关期刊/会议系列"
    assert i18n["zh-CN"]["sort.journalConference"] == "期刊/会议证据"


def test_static_ui_journal_conference_keys_are_wired_consistently() -> None:
    root = Path(__file__).resolve().parents[1]
    html = (root / "src" / "path_to_academia" / "webui" / "static" / "index.html").read_text(encoding="utf-8")
    js = (root / "src" / "path_to_academia" / "webui" / "static" / "app.js").read_text(encoding="utf-8")
    i18n = json.loads((root / "src" / "path_to_academia" / "webui" / "static" / "i18n.json").read_text(encoding="utf-8"))

    filter_contracts = {
        "targetJournalConference": "hasTargetJournalConference",
        "relatedJournalConference": "hasRelatedJournalConference",
    }
    for filter_key, row_flag in filter_contracts.items():
        assert f'data-filter="{filter_key}"' in html
        assert f'"filters.{filter_key}"' in json.dumps(i18n["en"])
        assert f"{filter_key}: false" in js
        assert f"state.filters.{filter_key}" in js
        assert f"!row.{row_flag}" in js
        assert f"row.{row_flag}" in js

    assert 'value="journalConference"' in html
    assert "sort === \"journalConference\"" in js
    assert "function journalConferenceScore(row)" in js
    assert "sort.journalConference" in i18n["en"]

    stale_fragments = ["targetVenue", "relatedVenue", "sort.venue", "venueScore"]
    surface = html + "\n" + js + "\n" + json.dumps(i18n)
    for fragment in stale_fragments:
        assert fragment not in surface
