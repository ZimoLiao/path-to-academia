from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .csvio import read_dicts
from .quality import person_key
from .status import ensure_status_file, upsert_status


STATIC = Path(__file__).resolve().parent / "webui" / "static"


class WorkspaceHandler(BaseHTTPRequestHandler):
    workspace: Path
    server_version = "PathToAcademia/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {self.address_string()} {fmt % args}")

    def send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_error_json(self, message: str, status: HTTPStatus) -> None:
        self.send_json({"error": message}, status)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        try:
            if path == "/api/health":
                self.handle_health()
            elif path == "/api/entities":
                self.handle_entities()
            elif path == "/api/status":
                self.handle_status()
            elif path == "/" or path == "/index.html":
                self.serve_file(STATIC / "index.html")
            elif path.startswith("/static/"):
                requested = (STATIC / path.removeprefix("/static/")).resolve()
                if STATIC.resolve() not in requested.parents and requested != STATIC.resolve():
                    self.send_error_json("invalid static path", HTTPStatus.BAD_REQUEST)
                    return
                self.serve_file(requested)
            else:
                self.send_error_json("not found", HTTPStatus.NOT_FOUND)
        except FileNotFoundError as exc:
            self.send_error_json(str(exc), HTTPStatus.INTERNAL_SERVER_ERROR)
        except Exception as exc:  # pragma: no cover - visible local diagnostic
            self.send_error_json(f"{type(exc).__name__}: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/status":
            self.send_error_json("not found", HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw or "{}")
            if not isinstance(payload, dict):
                raise ValueError("JSON body must be an object")
            updated = upsert_status(self.workspace, {str(key): str(value) for key, value in payload.items()})
            self.send_json({"record": updated})
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_error_json(str(exc), HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # pragma: no cover - visible local diagnostic
            self.send_error_json(f"{type(exc).__name__}: {exc}", HTTPStatus.INTERNAL_SERVER_ERROR)

    def entity_rows(self) -> list[dict[str, str]]:
        table = self.workspace / "tables" / "entities_final.csv"
        if not table.exists():
            raise FileNotFoundError(f"missing fact table: {table}")
        _, rows = read_dicts(table)
        for row in rows:
            row["person_key"] = person_key(row.get("name", ""), row.get("institution", ""))
        return rows

    def status_rows(self) -> list[dict[str, str]]:
        ensure_status_file(self.workspace)
        _, rows = read_dicts(self.workspace / "ui_state" / "outreach_status.csv")
        return rows

    def unmatched_status_rows(self, entities: list[dict[str, str]], statuses: list[dict[str, str]]) -> list[dict[str, str]]:
        known = {row["person_key"] for row in entities}
        return [row for row in statuses if row.get("person_key", "") not in known]

    def handle_health(self) -> None:
        entities = self.entity_rows()
        statuses = self.status_rows()
        self.send_json(
            {
                "status": "ok",
                "entity_count": len(entities),
                "status_count": len(statuses),
                "unmatched_status_count": len(self.unmatched_status_rows(entities, statuses)),
                "entity_table": "tables/entities_final.csv",
                "status_file": "ui_state/outreach_status.csv",
            }
        )

    def handle_entities(self) -> None:
        entities = self.entity_rows()
        self.send_json({"records": entities, "count": len(entities), "source": "tables/entities_final.csv"})

    def handle_status(self) -> None:
        entities = self.entity_rows()
        statuses = self.status_rows()
        self.send_json(
            {
                "records": statuses,
                "count": len(statuses),
                "unmatched": self.unmatched_status_rows(entities, statuses),
                "source": "ui_state/outreach_status.csv",
            }
        )

    def serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error_json(f"missing file: {path}", HTTPStatus.NOT_FOUND)
            return
        data = path.read_bytes()
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_handler(workspace: Path) -> type[WorkspaceHandler]:
    class BoundWorkspaceHandler(WorkspaceHandler):
        pass

    BoundWorkspaceHandler.workspace = workspace.resolve()
    return BoundWorkspaceHandler


def serve(workspace: Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    handler = make_handler(workspace)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"path to academia running at http://{host}:{port}/")
    print(f"Workspace: {workspace.resolve()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the path to academia web UI.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    serve(args.workspace, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
