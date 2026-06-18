from __future__ import annotations

import argparse
import json
from pathlib import Path

from .context import build_workspace_context
from .quality import run_quality_checks
from .status import upsert_status
from .web import serve
from .workspace import init_workspace
from .xlsx import write_xlsx


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="path-to-academia", description="path to academia CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Create a workspace")
    init_cmd.add_argument("workspace", type=Path)
    init_cmd.add_argument("--example", default="ml-bio", choices=["ml-bio", "empty"])
    init_cmd.add_argument("--force", action="store_true")

    qa_cmd = sub.add_parser("qa", help="Run workspace quality checks")
    qa_cmd.add_argument("workspace", type=Path)

    context_cmd = sub.add_parser("context", help="Print agent-ready workspace context")
    context_cmd.add_argument("workspace", type=Path)

    xlsx_cmd = sub.add_parser("export-xlsx", help="Create a wrapped XLSX from a CSV")
    xlsx_cmd.add_argument("csv_path", type=Path)
    xlsx_cmd.add_argument("xlsx_path", type=Path)

    status_cmd = sub.add_parser("status-upsert", help="Create or update a private status sidecar row")
    status_cmd.add_argument("workspace", type=Path)
    status_cmd.add_argument("--person-key")
    status_cmd.add_argument("--name")
    status_cmd.add_argument("--institution")
    status_cmd.add_argument("--status")
    status_cmd.add_argument("--priority")
    status_cmd.add_argument("--last-contacted")
    status_cmd.add_argument("--next-action-date")
    status_cmd.add_argument("--private-note")

    serve_cmd = sub.add_parser("serve", help="Run the local web UI")
    serve_cmd.add_argument("workspace", type=Path)
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8765)

    args = parser.parse_args(argv)
    if args.command == "init":
        init_workspace(args.workspace, example=args.example, force=args.force)
        print(args.workspace)
        return 0
    if args.command == "qa":
        report = run_quality_checks(args.workspace)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    if args.command == "context":
        context = build_workspace_context(args.workspace)
        print(json.dumps(context, indent=2, ensure_ascii=False))
        return 0
    if args.command == "export-xlsx":
        write_xlsx(args.csv_path, args.xlsx_path)
        print(args.xlsx_path)
        return 0
    if args.command == "status-upsert":
        payload = {
            key: value
            for key, value in {
                "person_key": args.person_key,
                "name": args.name,
                "institution": args.institution,
                "status": args.status,
                "priority": args.priority,
                "last_contacted": args.last_contacted,
                "next_action_date": args.next_action_date,
                "private_note": args.private_note,
            }.items()
            if value is not None
        }
        updated = upsert_status(
            args.workspace,
            payload,
        )
        print(json.dumps(updated, indent=2, ensure_ascii=False))
        return 0
    if args.command == "serve":
        serve(args.workspace, host=args.host, port=args.port)
        return 0
    parser.error("unknown command")
    return 2
