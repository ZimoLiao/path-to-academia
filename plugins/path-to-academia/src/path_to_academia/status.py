from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import schemas
from .csvio import read_dicts, write_dicts
from .quality import person_key


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_status_file(workspace: Path) -> None:
    path = workspace / "ui_state" / "outreach_status.csv"
    if path.exists():
        return
    write_dicts(path, schemas.STATUS_FIELDS, [])


def upsert_status(workspace: Path, payload: dict[str, str]) -> dict[str, str]:
    ensure_status_file(workspace)
    key = payload.get("person_key", "").strip()
    if not key:
        name = payload.get("name", "").strip()
        institution = payload.get("institution", "").strip()
        if not name or not institution:
            raise ValueError("status payload must include person_key or name and institution")
        key = person_key(name, institution)
    if not key:
        raise ValueError("status payload must include person_key or name and institution")

    _, rows = read_dicts(workspace / "ui_state" / "outreach_status.csv")
    existing = next((row for row in rows if row.get("person_key") == key), {})

    def value(field: str) -> str:
        return payload[field] if field in payload else existing.get(field, "")

    updated = {
        "person_key": key,
        "name": value("name"),
        "institution": value("institution"),
        "status": value("status"),
        "priority": value("priority"),
        "last_contacted": value("last_contacted"),
        "next_action_date": value("next_action_date"),
        "private_note": value("private_note"),
        "updated_at": now_iso(),
    }
    out: list[dict[str, str]] = []
    replaced = False
    for row in rows:
        if row.get("person_key") == key:
            out.append(updated)
            replaced = True
        else:
            out.append(row)
    if not replaced:
        out.append(updated)
    write_dicts(workspace / "ui_state" / "outreach_status.csv", schemas.STATUS_FIELDS, out)
    return updated
