const STATUS_OPTIONS = ["none", "to_apply", "shortlist", "contacted", "waiting_reply", "follow-up", "applied", "rejected"];

const LANGUAGE_NAMES = {
  en: "English",
  "zh-CN": "简体中文",
  "zh-TW": "繁體中文",
  ja: "日本語",
  ko: "한국어",
  fr: "Français",
  de: "Deutsch",
  es: "Español",
  "pt-BR": "Português",
};

const state = {
  records: [],
  statuses: new Map(),
  filtered: [],
  selectedKey: "",
  activeTag: "",
  language: "en",
  translations: {},
  filters: {
    targetJournalConference: false,
    relatedJournalConference: false,
    honors: false,
    missingMetrics: false,
    status: "",
  },
};

const els = {};

document.addEventListener("DOMContentLoaded", async () => {
  bindElements();
  await loadTranslations();
  initControls();
  boot();
});

function bindElements() {
  for (const id of [
    "languageSelect",
    "topStats",
    "searchInput",
    "minH",
    "minCites",
    "countrySelect",
    "sortSelect",
    "statusFilters",
    "tagTree",
    "resultSummary",
    "cards",
    "dossier",
    "clearFilters",
  ]) {
    els[id] = document.getElementById(id);
  }
}

async function loadTranslations() {
  const response = await fetch("/static/i18n.json", { cache: "no-store" });
  state.translations = await response.json();
  state.language = chooseInitialLanguage();
  document.documentElement.lang = state.language;
  renderLanguageSelect();
  applyStaticTranslations();
}

function chooseInitialLanguage() {
  const saved = localStorage.getItem("path-to-academia.language");
  if (saved && state.translations[saved]) return saved;
  const browserLanguages = navigator.languages?.length ? navigator.languages : [navigator.language || "en"];
  for (const raw of browserLanguages) {
    if (state.translations[raw]) return raw;
    const base = raw.split("-")[0];
    if (base === "zh") return state.translations["zh-CN"] ? "zh-CN" : "en";
    const match = Object.keys(state.translations).find((code) => code.split("-")[0] === base);
    if (match) return match;
  }
  return "en";
}

function renderLanguageSelect() {
  els.languageSelect.innerHTML = Object.keys(state.translations)
    .map((code) => `<option value="${escapeAttr(code)}">${escapeHtml(LANGUAGE_NAMES[code] || code)}</option>`)
    .join("");
  els.languageSelect.value = state.language;
  els.languageSelect.addEventListener("change", () => {
    state.language = els.languageSelect.value;
    localStorage.setItem("path-to-academia.language", state.language);
    document.documentElement.lang = state.language;
    applyStaticTranslations();
    renderStatusFilters();
    populateCountries();
    applyFilters();
  });
}

function applyStaticTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });
}

function t(key, vars = {}) {
  const table = state.translations[state.language] || state.translations.en || {};
  const fallback = state.translations.en || {};
  const template = table[key] || fallback[key] || key;
  return template.replace(/\{(\w+)\}/g, (_, name) => String(vars[name] ?? ""));
}

function initControls() {
  document.querySelectorAll(".toggle[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.filter;
      state.filters[key] = !state.filters[key];
      button.classList.toggle("is-active", state.filters[key]);
      applyFilters();
    });
  });

  for (const control of [els.searchInput, els.minH, els.minCites, els.countrySelect, els.sortSelect]) {
    control.addEventListener("input", applyFilters);
    control.addEventListener("change", applyFilters);
  }
  els.clearFilters.addEventListener("click", clearFilters);
  renderStatusFilters();
}

async function boot() {
  try {
    const [recordsResponse, statusResponse] = await Promise.all([fetch("/api/entities"), fetch("/api/status")]);
    const records = await recordsResponse.json();
    const statuses = await statusResponse.json();
    if (!recordsResponse.ok) throw new Error(records.error || "Could not load records");
    if (!statusResponse.ok) throw new Error(statuses.error || "Could not load private status");

    state.statuses = new Map((statuses.records || []).map((row) => [row.person_key, row]));
    state.records = (records.records || []).map(enrichRecord);
    state.selectedKey = state.records[0]?.person_key || "";
    populateCountries();
    applyFilters();
  } catch (error) {
    els.topStats.innerHTML = `<span class="stat-pill">${escapeHtml(t("message.error", { message: error.message }))}</span>`;
    els.cards.innerHTML = `<div class="empty">${escapeHtml(t("empty.failedLoad", { message: error.message }))}</div>`;
  }
}

function enrichRecord(row) {
  const status = state.statuses.get(row.person_key) || {};
  const tags = splitTags(row.domain_tags);
  const hNum = numberValue(row.h_index);
  const citeNum = numberValue(row.citation_count);
  return {
    ...row,
    tags,
    status: status.status || "none",
    priority: status.priority || "",
    last_contacted: status.last_contacted || "",
    next_action_date: status.next_action_date || "",
    private_note: status.private_note || "",
    hNum,
    citeNum,
    hasTargetJournalConference: yesish(row.target_venue_exact),
    hasRelatedJournalConference: yesish(row.target_venue_family),
    hasHonors: Boolean(clean(row.honors)),
    missingMetrics: hNum === null || citeNum === null,
  };
}

function searchableText(row) {
  return [
    row.name,
    row.role_title,
    row.institution,
    row.department_or_group,
    row.country,
    row.summary_text,
    row.domain_tags,
    row.honors,
    row.target_publication_evidence,
    row.relevance_reason,
    row.relevance_evidence,
    row.source_name,
    row.source_url,
    row.all_source_names,
    row.all_source_urls,
    row.notes,
  ]
    .join(" ")
    .toLowerCase();
}

function populateCountries() {
  const current = els.countrySelect.value;
  const countries = [...new Set(state.records.map((row) => row.country).filter(Boolean))].sort();
  els.countrySelect.innerHTML = `<option value="">${escapeHtml(t("filters.allCountries"))}</option>${countries
    .map((country) => `<option value="${escapeAttr(country)}">${escapeHtml(country)}</option>`)
    .join("")}`;
  if (countries.includes(current)) els.countrySelect.value = current;
}

function renderStatusFilters() {
  els.statusFilters.innerHTML = STATUS_OPTIONS.map(
    (status) => `<button class="status-button" data-status="${status}">${escapeHtml(labelStatus(status))}</button>`,
  ).join("");
  els.statusFilters.querySelectorAll(".status-button").forEach((button) => {
    button.classList.toggle("is-active", state.filters.status === button.dataset.status);
    button.addEventListener("click", () => {
      const value = button.dataset.status;
      state.filters.status = state.filters.status === value ? "" : value;
      renderStatusFilters();
      applyFilters();
    });
  });
}

function clearFilters() {
  state.activeTag = "";
  state.filters = {
    targetJournalConference: false,
    relatedJournalConference: false,
    honors: false,
    missingMetrics: false,
    status: "",
  };
  els.searchInput.value = "";
  els.minH.value = "";
  els.minCites.value = "";
  els.countrySelect.value = "";
  els.sortSelect.value = "fit";
  document.querySelectorAll(".toggle[data-filter]").forEach((button) => button.classList.remove("is-active"));
  renderStatusFilters();
  applyFilters();
}

function applyFilters() {
  const query = els.searchInput.value.trim().toLowerCase();
  const minH = numberValue(els.minH.value);
  const minCites = numberValue(els.minCites.value);
  const country = els.countrySelect.value;

  state.filtered = state.records.filter((row) => {
    if (query && !searchableText(row).includes(query)) return false;
    if (state.activeTag && !row.tags.includes(state.activeTag)) return false;
    if (country && row.country !== country) return false;
    if (state.filters.targetJournalConference && !row.hasTargetJournalConference) return false;
    if (state.filters.relatedJournalConference && !row.hasRelatedJournalConference) return false;
    if (state.filters.honors && !row.hasHonors) return false;
    if (state.filters.missingMetrics && !row.missingMetrics) return false;
    if (state.filters.status && row.status !== state.filters.status) return false;
    if (minH !== null && (row.hNum === null || row.hNum < minH)) return false;
    if (minCites !== null && (row.citeNum === null || row.citeNum < minCites)) return false;
    return true;
  });

  sortRows();
  if (!state.filtered.some((row) => row.person_key === state.selectedKey)) {
    state.selectedKey = state.filtered[0]?.person_key || state.records[0]?.person_key || "";
  }
  renderAll();
}

function sortRows() {
  const sort = els.sortSelect.value;
  state.filtered.sort((a, b) => {
    if (sort === "h") return compareNum(b.hNum, a.hNum) || a.name.localeCompare(b.name);
    if (sort === "citations") return compareNum(b.citeNum, a.citeNum) || a.name.localeCompare(b.name);
    if (sort === "journalConference") return journalConferenceScore(b) - journalConferenceScore(a) || compareNum(b.hNum, a.hNum) || a.name.localeCompare(b.name);
    if (sort === "country") return a.country.localeCompare(b.country) || a.name.localeCompare(b.name);
    if (sort === "status") return a.status.localeCompare(b.status) || a.name.localeCompare(b.name);
    if (sort === "name") return a.name.localeCompare(b.name);
    return fitScore(b) - fitScore(a) || compareNum(b.hNum, a.hNum) || a.name.localeCompare(b.name);
  });
}

function renderAll() {
  renderTopStats();
  renderTagTree();
  renderCards();
  renderDossier();
}

function renderTopStats() {
  const exact = state.records.filter((row) => row.hasTargetJournalConference).length;
  const family = state.records.filter((row) => row.hasRelatedJournalConference).length;
  const statusCount = [...state.statuses.values()].filter((row) => row.status && row.status !== "none").length;
  const countries = new Set(state.records.map((row) => row.country).filter(Boolean)).size;
  els.topStats.innerHTML = [
    t("top.records", { count: state.records.length }),
    t("top.shown", { count: state.filtered.length }),
    t("top.countries", { count: countries }),
    t("top.targetJournalConference", { count: exact }),
    t("top.relatedJournalConference", { count: family }),
    t("top.statusRows", { count: statusCount }),
  ]
    .map((text) => `<span class="stat-pill">${escapeHtml(text)}</span>`)
    .join("");
}

function renderTagTree() {
  const tags = [...new Set(state.records.flatMap((row) => row.tags))].sort((a, b) => tagCount(b) - tagCount(a) || a.localeCompare(b));
  if (!tags.length) {
    els.tagTree.innerHTML = `<div class="empty">${escapeHtml(t("empty.noTags"))}</div>`;
    return;
  }
  els.tagTree.innerHTML = tags
    .map((tag) => {
      const count = state.records.filter((row) => tagMatchesCurrentFilters(row, tag)).length;
      return `
        <button class="tag-node ${state.activeTag === tag ? "is-active" : ""}" data-tag="${escapeAttr(tag)}">
          <span>${escapeHtml(tag)}</span>
          <strong>${count}</strong>
        </button>
      `;
    })
    .join("");
  els.tagTree.querySelectorAll(".tag-node").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeTag = state.activeTag === button.dataset.tag ? "" : button.dataset.tag;
      applyFilters();
    });
  });
}

function tagMatchesCurrentFilters(row, tag) {
  if (!row.tags.includes(tag)) return false;
  const activeTag = state.activeTag;
  state.activeTag = "";
  const query = els.searchInput.value.trim().toLowerCase();
  const minH = numberValue(els.minH.value);
  const minCites = numberValue(els.minCites.value);
  const country = els.countrySelect.value;
  const ok =
    (!query || searchableText(row).includes(query)) &&
    (!country || row.country === country) &&
    (!state.filters.targetJournalConference || row.hasTargetJournalConference) &&
    (!state.filters.relatedJournalConference || row.hasRelatedJournalConference) &&
    (!state.filters.honors || row.hasHonors) &&
    (!state.filters.missingMetrics || row.missingMetrics) &&
    (!state.filters.status || row.status === state.filters.status) &&
    (minH === null || (row.hNum !== null && row.hNum >= minH)) &&
    (minCites === null || (row.citeNum !== null && row.citeNum >= minCites));
  state.activeTag = activeTag;
  return ok;
}

function renderCards() {
  els.resultSummary.textContent = t("records.summary", { shown: state.filtered.length, total: state.records.length });
  if (!state.filtered.length) {
    els.cards.innerHTML = `<div class="empty">${escapeHtml(t("empty.noRecords"))}</div>`;
    return;
  }
  els.cards.innerHTML = state.filtered.map(renderCard).join("");
  els.cards.querySelectorAll(".card").forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("a, button, input, select, textarea")) return;
      state.selectedKey = card.dataset.key;
      renderCards();
      renderDossier();
    });
  });
  els.cards.querySelectorAll("[data-evidence-section]").forEach((control) => {
    control.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      state.selectedKey = control.dataset.key;
      renderCards();
      renderDossier();
      focusDossierSection(control.dataset.evidenceSection);
    });
  });
}

function renderCard(row) {
  const badges = [
    row.hasTargetJournalConference ? evidenceBadge(row, "targetPublication", t("badge.targetJournalConference")) : "",
    row.hasRelatedJournalConference ? evidenceBadge(row, "targetPublication", t("badge.relatedJournalConference")) : "",
    row.hasHonors ? evidenceBadge(row, "honors", t("badge.honors")) : "",
  ].join("");
  return `
    <article class="card ${row.person_key === state.selectedKey ? "is-selected" : ""}" data-key="${escapeAttr(row.person_key)}">
      <div class="card__head">
        <h2>${escapeHtml(row.name)}</h2>
        <span class="status-badge" data-status="${escapeAttr(row.status)}">${escapeHtml(labelStatus(row.status))}</span>
      </div>
      <div class="meta">${escapeHtml(row.institution)} · ${escapeHtml(row.country)}</div>
      <p>${escapeHtml(truncate(row.summary_text, 230))}</p>
      <div class="tag-row">${row.tags.map(tagPill).join("")}${badges}</div>
      <div class="metrics-line">
        <span>${escapeHtml(t("metric.h"))} ${escapeHtml(row.h_index || "NA")}</span>
        <span>${escapeHtml(t("metric.citations"))} ${escapeHtml(formatNumber(row.citation_count) || "NA")}</span>
      </div>
      ${renderCardActions(row)}
    </article>
  `;
}

function renderDossier() {
  const row = state.records.find((record) => record.person_key === state.selectedKey);
  if (!row) {
    els.dossier.innerHTML = `<p class="empty">${escapeHtml(t("empty.noSelected"))}</p>`;
    return;
  }
  els.dossier.innerHTML = `
    <div class="panel__title">${escapeHtml(t("dossier.title"))}</div>
    <h2>${escapeHtml(row.name)}</h2>
    <div class="meta">${escapeHtml(row.role_title || t("entity.researcher"))} · ${escapeHtml(row.institution)} · ${escapeHtml(row.country)}</div>
    ${linkRow(row)}
    <div class="tag-row">${row.tags.map(tagPill).join("")}${row.hasTargetJournalConference ? `<span class="badge">${escapeHtml(t("badge.targetJournalConference"))}</span>` : ""}${row.hasRelatedJournalConference ? `<span class="badge">${escapeHtml(t("badge.relatedJournalConference"))}</span>` : ""}</div>

    <section class="dossier-section">
      <div class="dossier-section__title">${escapeHtml(t("dossier.privateStatus"))}</div>
      ${renderStatusEditor(row)}
    </section>

    ${section(t("dossier.group"), row.department_or_group, "group")}
    ${section(t("dossier.summary"), row.summary_text, "summary")}
    ${section(t("dossier.relevanceEvidence"), row.relevance_evidence || row.relevance_reason, "relevanceEvidence")}
    ${section(t("dossier.honors"), row.honors, "honors")}
    ${section(t("dossier.metrics"), metricsText(row), "metrics")}
    ${section(t("dossier.targetPublication"), row.target_publication_evidence, "targetPublication")}
    ${section(t("dossier.notes"), row.notes, "notes")}
    ${sourceSection(row)}
  `;
  bindDossierControls(row);
}

function renderStatusEditor(row) {
  return `
    <div class="status-editor">
      <div class="button-grid">
        ${STATUS_OPTIONS.map(
          (status) => `<button class="status-button ${row.status === status ? "is-active" : ""}" data-edit-status="${status}">${escapeHtml(labelStatus(status))}</button>`,
        ).join("")}
      </div>
      <label class="field field--compact">
        <span>${escapeHtml(t("label.priority"))}</span>
        <select id="priorityInput">
          ${["", "high", "medium", "low"].map((value) => `<option value="${value}" ${row.priority === value ? "selected" : ""}>${escapeHtml(labelPriority(value))}</option>`).join("")}
        </select>
      </label>
      <label class="field field--compact">
        <span>${escapeHtml(t("label.lastContacted"))}</span>
        <input id="lastContactedInput" name="last_contacted" type="date" value="${escapeAttr(row.last_contacted || "")}" />
      </label>
      <label class="field field--compact">
        <span>${escapeHtml(t("label.nextAction"))}</span>
        <input id="nextActionInput" name="next_action_date" type="date" value="${escapeAttr(row.next_action_date || "")}" />
      </label>
      <label class="field field--compact">
        <span>${escapeHtml(t("label.privateNote"))}</span>
        <textarea id="privateNoteInput" rows="4">${escapeHtml(row.private_note || "")}</textarea>
      </label>
      <div class="save-row">
        <button id="saveStatus" class="clear-button">${escapeHtml(t("button.saveStatus"))}</button>
        <span id="saveMessage" class="save-message"></span>
      </div>
    </div>
  `;
}

function bindDossierControls(row) {
  let draftStatus = row.status || "none";
  els.dossier.querySelectorAll("[data-edit-status]").forEach((button) => {
    button.addEventListener("click", () => {
      draftStatus = button.dataset.editStatus;
      els.dossier.querySelectorAll("[data-edit-status]").forEach((item) => item.classList.toggle("is-active", item === button));
    });
  });

  document.getElementById("saveStatus").addEventListener("click", async () => {
    const message = document.getElementById("saveMessage");
    message.textContent = t("message.saving");
    const payload = {
      person_key: row.person_key,
      name: row.name,
      institution: row.institution,
      status: draftStatus,
      priority: document.getElementById("priorityInput").value,
      last_contacted: document.getElementById("lastContactedInput").value,
      next_action_date: document.getElementById("nextActionInput").value,
      private_note: document.getElementById("privateNoteInput").value,
    };
    try {
      const response = await fetch("/api/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || t("message.saveFailed"));
      state.statuses.set(row.person_key, data.record);
      state.records = state.records.map((record) => (record.person_key === row.person_key ? enrichRecord(record) : record));
      message.textContent = t("message.saved");
      applyFilters();
    } catch (error) {
      message.textContent = t("message.error", { message: error.message });
    }
  });
}

function section(title, value, sectionName = "") {
  if (!clean(value)) return "";
  const sectionAttrs = sectionName
    ? ` id="${escapeAttr(dossierSectionId(sectionName))}" data-dossier-section="${escapeAttr(sectionName)}"`
    : "";
  return `
    <section class="dossier-section"${sectionAttrs}>
      <div class="dossier-section__title">${escapeHtml(title)}</div>
      <div class="dossier-text">${linkifyText(value)}</div>
    </section>
  `;
}

function linkRow(row) {
  const all = profileLinks(row, { includeExtraSources: true });
  if (!all.length) return "";
  return `<div class="link-row">${renderLinks(all)}</div>`;
}

function renderCardActions(row) {
  const links = profileLinks(row, { includeExtraSources: false });
  if (!links.length) return "";
  return `<div class="card-actions link-row">${renderLinks(links)}</div>`;
}

function profileLinks(row, options = {}) {
  const links = [
    [t("link.homepage"), row.homepage_url],
    [t("link.orcid"), row.orcid_url],
    [t("link.scholar"), row.scholar_url],
    [t("link.openalex"), row.openalex_url],
    [t("link.semanticScholar"), row.semantic_scholar_url],
    [t("link.primarySource"), row.source_url],
  ].filter(([, href]) => clean(href) && /^https?:\/\//.test(href));
  if (!options.includeExtraSources) return dedupeLinks(links);
  const extra = (row.all_source_urls || "")
    .split(";")
    .map((item) => item.trim())
    .filter((href) => /^https?:\/\//.test(href))
    .slice(0, 4)
    .map((href, index) => [t("link.sourceNumber", { count: index + 1 }), href]);
  return dedupeLinks([...links, ...extra]);
}

function renderLinks(links) {
  return links.map(([label, href]) => `<a href="${escapeAttr(href)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`).join("");
}

function evidenceBadge(row, sectionName, label) {
  const preview = sectionName === "honors" ? row.honors : row.target_publication_evidence;
  const title = clean(preview) || label;
  return `<button type="button" class="badge badge-button" data-key="${escapeAttr(row.person_key)}" data-evidence-section="${escapeAttr(sectionName)}" title="${escapeAttr(title)}" aria-label="${escapeAttr(`${label}: ${row.name}`)}">${escapeHtml(label)}</button>`;
}

function sourceSection(row) {
  const links = sourceLinks(row);
  const sourceNames = [row.source_name, row.all_source_names].filter(clean).join("\n");
  if (!clean(sourceNames) && !links.length) return "";
  return `
    <section class="dossier-section" id="${escapeAttr(dossierSectionId("sourceProvenance"))}" data-dossier-section="sourceProvenance">
      <div class="dossier-section__title">${escapeHtml(t("dossier.sourceProvenance"))}</div>
      ${clean(sourceNames) ? `<div class="dossier-text">${linkifyText(sourceNames)}</div>` : ""}
      ${links.length ? `<div class="source-list link-row">${renderLinks(links)}</div>` : ""}
    </section>
  `;
}

function sourceLinks(row) {
  const names = splitList(row.all_source_names);
  const links = [];
  if (clean(row.source_url) && /^https?:\/\//.test(row.source_url)) {
    links.push([row.source_name || t("link.primarySource"), row.source_url]);
  }
  splitList(row.all_source_urls)
    .filter((href) => /^https?:\/\//.test(href))
    .forEach((href, index) => {
      links.push([names[index] || t("link.sourceNumber", { count: index + 1 }), href]);
    });
  return dedupeLinks(links);
}

function dedupeLinks(links) {
  const seen = new Set();
  return links.filter(([, href]) => {
    const key = clean(href);
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function linkifyText(value) {
  const text = clean(value);
  const pattern = /https?:\/\/[^\s<>"']+/g;
  let html = "";
  let lastIndex = 0;
  for (const match of text.matchAll(pattern)) {
    html += formatPlainText(text.slice(lastIndex, match.index));
    const { href, suffix } = trimUrlSuffix(match[0]);
    html += `<a href="${escapeAttr(href)}" target="_blank" rel="noreferrer">${escapeHtml(href)}</a>${formatPlainText(suffix)}`;
    lastIndex = match.index + match[0].length;
  }
  html += formatPlainText(text.slice(lastIndex));
  return html;
}

function trimUrlSuffix(raw) {
  let href = raw;
  let suffix = "";
  while (/[),.;\]]$/.test(href)) {
    suffix = href.slice(-1) + suffix;
    href = href.slice(0, -1);
  }
  return { href, suffix };
}

function formatPlainText(value) {
  return escapeHtml(value).replace(/\n/g, "<br />");
}

function focusDossierSection(sectionName) {
  const section = document.getElementById(dossierSectionId(sectionName));
  if (!section) return;
  section.scrollIntoView({ block: "nearest", behavior: "smooth" });
  section.classList.add("is-highlighted");
  window.setTimeout(() => section.classList.remove("is-highlighted"), 900);
}

function metricsText(row) {
  return [
    `${t("metrics.hIndex")}: ${row.h_index || t("metrics.missing")}`,
    `${t("metrics.citationCount")}: ${formatNumber(row.citation_count) || t("metrics.missing")}`,
    row.metric_source ? `${t("metrics.metricSource")}: ${row.metric_source}` : "",
  ]
    .filter(Boolean)
    .join("\n");
}

function dossierSectionId(sectionName) {
  return `dossier-section-${String(sectionName || "").replace(/[^a-z0-9_-]/gi, "-")}`;
}

function fitScore(row) {
  let score = 0;
  score += row.tags.length * 4;
  score += journalConferenceScore(row) * 12;
  if (row.hasHonors) score += 8;
  if (row.status === "shortlist") score += 10;
  if (row.status === "rejected") score -= 30;
  score += Math.min(row.hNum || 0, 80) / 10;
  return score;
}

function journalConferenceScore(row) {
  return (row.hasTargetJournalConference ? 2 : 0) + (row.hasRelatedJournalConference ? 1 : 0);
}

function tagCount(tag) {
  return state.records.filter((row) => row.tags.includes(tag)).length;
}

function tagPill(tag) {
  return `<span class="pill">${escapeHtml(tag)}</span>`;
}

function splitTags(value) {
  return String(value || "")
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean);
}

function splitList(value) {
  return String(value || "")
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean);
}

function yesish(value) {
  return ["yes", "true", "1", "y"].includes(String(value || "").trim().toLowerCase());
}

function compareNum(a, b) {
  if (a === null && b === null) return 0;
  if (a === null) return -1;
  if (b === null) return 1;
  return a - b;
}

function numberValue(value) {
  const match = String(value || "").replaceAll(",", "").match(/\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
}

function formatNumber(value) {
  const n = numberValue(value);
  return n === null ? "" : new Intl.NumberFormat(state.language).format(n);
}

function truncate(value, max) {
  const text = clean(value);
  if (text.length <= max) return text;
  return `${text.slice(0, max - 1)}...`;
}

function labelStatus(status) {
  if (!status || status === "none") return t("status.none");
  return t(`status.${status}`) || status;
}

function labelPriority(priority) {
  if (!priority) return t("priority.unset");
  return t(`priority.${priority}`) || priority;
}

function clean(value) {
  return String(value || "").trim();
}

function escapeHtml(value) {
  return clean(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/"/g, "&quot;");
}
