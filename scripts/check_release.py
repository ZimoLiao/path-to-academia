#!/usr/bin/env python3
from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = "path-to-academia"
PLUGIN_BUNDLE = ROOT / "plugins" / PLUGIN_NAME
PLUGIN_SOURCE_PATH = f"./plugins/{PLUGIN_NAME}"
RUNTIME_SCRIPT_NAMES = [
    "_bootstrap.py",
    "init_workspace.py",
    "qa_workspace.py",
    "workspace_context.py",
    "export_wrapped_xlsx.py",
    "serve_web.py",
]


def is_generated_path(path: Path) -> bool:
    return (
        path.name == "build"
        or path.name.endswith(".egg-info")
        or path.suffix == ".pyc"
        or "__pycache__" in path.parts
        or path.name == ".pytest_cache"
    )


def project_version() -> str:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, flags=re.MULTILINE)
    if not match:
        raise SystemExit("pyproject.toml does not declare a project version")
    return match.group(1)


def text_version(path: Path, pattern: str, label: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        rel = path.relative_to(ROOT)
        raise SystemExit(f"{rel} does not declare {label}")
    return match.group(1)


def run(cmd: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> None:
    printable = " ".join(cmd)
    print(f"==> {printable}")
    subprocess.run(cmd, cwd=cwd or ROOT, env=env, check=True)


def run_json(cmd: list[str], *, cwd: Path | None = None) -> dict[str, object]:
    printable = " ".join(cmd)
    print(f"==> {printable}")
    result = subprocess.run(cmd, cwd=cwd or ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    payload = json.loads(result.stdout)
    if not isinstance(payload, dict):
        raise SystemExit(f"expected JSON object from {printable}")
    return payload


def clean_generated() -> None:
    for path in [
        ROOT / "build",
        PLUGIN_BUNDLE / "build",
        ROOT / "src" / "path_to_academia.egg-info",
        PLUGIN_BUNDLE / "src" / "path_to_academia.egg-info",
        ROOT / ".pytest_cache",
    ]:
        if path.exists():
            shutil.rmtree(path)
    for cache in ROOT.rglob("__pycache__"):
        shutil.rmtree(cache)


def clean_plugin_bundle_generated() -> None:
    for path in [PLUGIN_BUNDLE / "build", PLUGIN_BUNDLE / "src" / "path_to_academia.egg-info"]:
        if path.exists():
            shutil.rmtree(path)
    for cache in PLUGIN_BUNDLE.rglob("__pycache__"):
        shutil.rmtree(cache)


def python_files() -> list[str]:
    return [str(path.relative_to(ROOT)) for base in ["src", "scripts"] for path in (ROOT / base).rglob("*.py")]


def validate_versions() -> None:
    version = project_version()
    version_sources = {
        ROOT / "README.md": (r"Current release:\s*`([^`]+)`", "current release"),
        ROOT / "src" / "path_to_academia" / "__init__.py": (r'__version__\s*=\s*"([^"]+)"', "__version__"),
        PLUGIN_BUNDLE / "src" / "path_to_academia" / "__init__.py": (r'__version__\s*=\s*"([^"]+)"', "__version__"),
        ROOT / "CITATION.cff": (r'^version:\s*"([^"]+)"', "citation version"),
        PLUGIN_BUNDLE / "CITATION.cff": (r'^version:\s*"([^"]+)"', "citation version"),
        PLUGIN_BUNDLE / "pyproject.toml": (r'^version\s*=\s*"([^"]+)"', "project version"),
    }
    for path, (pattern, label) in version_sources.items():
        found = text_version(path, pattern, label)
        if found != version:
            rel = path.relative_to(ROOT)
            raise SystemExit(f"{rel} {label} mismatch: {found!r}")
    manifest_paths = [
        ROOT / ".codex-plugin" / "plugin.json",
        ROOT / ".claude-plugin" / "plugin.json",
        PLUGIN_BUNDLE / ".codex-plugin" / "plugin.json",
        PLUGIN_BUNDLE / ".claude-plugin" / "plugin.json",
    ]
    for manifest_path in manifest_paths:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("version") != version:
            rel = manifest_path.relative_to(ROOT)
            raise SystemExit(f"{rel} version mismatch: {manifest.get('version')!r}")
    codex_manifest = json.loads((PLUGIN_BUNDLE / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    claude_marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    if claude_marketplace.get("metadata", {}).get("version") != version:
        raise SystemExit(f"Claude marketplace version mismatch: {claude_marketplace.get('metadata')!r}")
    claude_entries = [entry for entry in claude_marketplace.get("plugins", []) if entry.get("name") == PLUGIN_NAME]
    if len(claude_entries) != 1 or claude_entries[0].get("source") != PLUGIN_SOURCE_PATH:
        raise SystemExit(f"Claude marketplace source mismatch: {claude_entries!r}")
    codex_marketplace = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
    codex_entries = [entry for entry in codex_marketplace.get("plugins", []) if entry.get("name") == PLUGIN_NAME]
    if len(codex_entries) != 1:
        raise SystemExit(f"Codex marketplace entry mismatch: {codex_entries!r}")
    codex_source = codex_entries[0].get("source", {})
    if codex_source.get("source") != "local" or codex_source.get("path") != PLUGIN_SOURCE_PATH:
        raise SystemExit(f"Codex marketplace source mismatch: {codex_source!r}")
    prompts = codex_manifest.get("interface", {}).get("defaultPrompt", [])
    if len(prompts) > 3:
        raise SystemExit("plugin.json has more than three default prompts")


def validate_plugin_bundle() -> None:
    required = [
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
        "skills/path-to-academia/SKILL.md",
        "docs/workflow.md",
        "docs/schema.md",
        "scripts/init_workspace.py",
        "src/path_to_academia/cli.py",
        "src/path_to_academia/webui/static/index.html",
        "pyproject.toml",
        "README.md",
        "AGENTS.md",
        "LICENSE",
    ]
    missing = [rel for rel in required if not (PLUGIN_BUNDLE / rel).exists()]
    if missing:
        raise SystemExit(f"plugin bundle missing files: {missing}")
    if (PLUGIN_BUNDLE / "scripts" / "check_release.py").exists():
        raise SystemExit("plugin bundle must not include scripts/check_release.py")
    generated = []
    for path in sorted(PLUGIN_BUNDLE.rglob("*")):
        if is_generated_path(path):
            generated.append(path.relative_to(ROOT).as_posix())
    if generated:
        raise SystemExit("plugin bundle contains generated files:\n" + "\n".join(generated))

    copied_files: list[str] = []
    for base in ["docs", "examples", "skills", "src"]:
        copied_files.extend(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / base).rglob("*")
            if path.is_file() and not is_generated_path(path)
        )
    copied_files.extend(f"scripts/{name}" for name in RUNTIME_SCRIPT_NAMES)
    copied_files.extend(
        [
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            "pyproject.toml",
            "CHANGELOG.md",
            "LICENSE",
            "SECURITY.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "CITATION.cff",
        ]
    )
    drifted = []
    for rel in copied_files:
        root_file = ROOT / rel
        bundle_file = PLUGIN_BUNDLE / rel
        if not bundle_file.exists() or not filecmp.cmp(root_file, bundle_file, shallow=False):
            drifted.append(rel)
    if drifted:
        raise SystemExit("plugin bundle is out of sync:\n" + "\n".join(drifted))


def validate_i18n() -> None:
    i18n_path = ROOT / "src" / "path_to_academia" / "webui" / "static" / "i18n.json"
    translations = json.loads(i18n_path.read_text(encoding="utf-8"))
    expected = {"en", "zh-CN", "zh-TW", "ja", "ko", "fr", "de", "es", "pt-BR"}
    missing = sorted(expected - set(translations))
    if missing:
        raise SystemExit(f"missing i18n languages: {missing}")
    english_keys = set(translations["en"])
    for language, values in translations.items():
        if set(values) != english_keys:
            raise SystemExit(f"i18n key mismatch for {language}")


def validate_residue() -> None:
    patterns = ["Atlas", "atlas", r"\baoa\b", "aoa_", "serve_atlas", "topCited", "top_cited", "TODO", "FIXME"]
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part.startswith(".git") for part in path.parts):
            continue
        if path.parts[-1] in {"benchmark-audit.md", "check_release.py"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if any(pattern.replace(r"\b", "") in line for pattern in patterns if "\\" not in pattern):
                rel = path.relative_to(ROOT).as_posix()
                hits.append(f"{rel}:{line_no}:    {line.strip()}")
            elif "aoa" in line.lower().split():
                rel = path.relative_to(ROOT).as_posix()
                hits.append(f"{rel}:{line_no}:    {line.strip()}")
    def allowed_hit(hit: str) -> bool:
        return hit.startswith("tests/test_web.py:") and '"Academic Opportunity " + "Atlas" not in surface' in hit

    unexpected = [hit for hit in hits if not allowed_hit(hit)]
    if unexpected:
        raise SystemExit("unexpected stale residue:\n" + "\n".join(unexpected))


def validate_codex(skip_codex: bool, strict_codex: bool) -> None:
    if skip_codex:
        print("==> codex validators skipped")
        return
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    skill_validator = codex_home / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    plugin_validator = codex_home / "skills" / ".system" / "plugin-creator" / "scripts" / "validate_plugin.py"
    missing = [path for path in [skill_validator, plugin_validator] if not path.exists()]
    if missing:
        message = "codex validators unavailable: " + ", ".join(str(path) for path in missing)
        if strict_codex:
            raise SystemExit(message)
        print(f"==> {message}; skipped")
        return
    run([sys.executable, str(skill_validator), "skills/path-to-academia"])
    run([sys.executable, str(skill_validator), "plugins/path-to-academia/skills/path-to-academia"])
    run([sys.executable, str(plugin_validator), "."])
    run([sys.executable, str(plugin_validator), "plugins/path-to-academia"])


def validate_claude(skip_claude: bool, strict_claude: bool) -> None:
    if skip_claude:
        print("==> Claude Code validator skipped")
        return
    claude = shutil.which("claude")
    if not claude:
        message = "Claude Code CLI unavailable; skipped claude plugin validate"
        if strict_claude:
            raise SystemExit(message)
        print(f"==> {message}")
        return
    run([claude, "plugin", "validate", "."])
    run([claude, "plugin", "validate", "plugins/path-to-academia"])


def validate_claude_install_script() -> None:
    with tempfile.TemporaryDirectory(prefix="path-to-academia-claude-home-") as tmp:
        env = dict(os.environ)
        env["HOME"] = tmp
        run(["bash", "-n", "install-claude.sh"])
        run(["bash", "install-claude.sh"], env=env)
        if shutil.which("claude"):
            result = subprocess.run(
                ["claude", "plugin", "list"],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            if "path-to-academia@path-to-academia" not in result.stdout or "enabled" not in result.stdout:
                raise SystemExit(f"Claude plugin list missing installed plugin:\n{result.stdout}")
        else:
            link = Path(tmp) / ".claude" / "skills" / "path-to-academia"
            if link.resolve() != PLUGIN_BUNDLE.resolve():
                raise SystemExit(f"Claude install symlink mismatch: {link} -> {link.resolve()}")


def validate_codex_install_script() -> None:
    with tempfile.TemporaryDirectory(prefix="path-to-academia-codex-home-") as tmp:
        env = dict(os.environ)
        env["HOME"] = tmp
        env["PATH"] = "/usr/bin:/bin"
        run(["bash", "-n", "install.sh"])
        run(["bash", "install.sh"], env=env)
        marketplace = Path(tmp) / ".agents" / "plugins" / "marketplace.json"
        data = json.loads(marketplace.read_text(encoding="utf-8"))
        entries = [entry for entry in data.get("plugins", []) if entry.get("name") == "path-to-academia"]
        if len(entries) != 1:
            raise SystemExit(f"Codex marketplace entry mismatch: {entries!r}")
        source = entries[0].get("source", {})
        if source.get("source") != "local" or source.get("path") != PLUGIN_SOURCE_PATH:
            raise SystemExit(f"Codex marketplace source mismatch: {source!r}")
        link = Path(tmp) / "plugins" / "path-to-academia"
        if link.resolve() != PLUGIN_BUNDLE.resolve():
            raise SystemExit(f"Codex install symlink mismatch: {link} -> {link.resolve()}")


def validate_codex_marketplace_cli(skip_codex: bool, strict_codex: bool) -> None:
    if skip_codex:
        print("==> codex marketplace install skipped")
        return
    codex = shutil.which("codex")
    if not codex:
        message = "Codex CLI unavailable; skipped native marketplace install"
        if strict_codex:
            raise SystemExit(message)
        print(f"==> {message}")
        return
    with tempfile.TemporaryDirectory(prefix="path-to-academia-codex-native-home-") as tmp:
        env = dict(os.environ)
        env["HOME"] = tmp
        run([codex, "plugin", "marketplace", "add", str(ROOT)], env=env)
        run([codex, "plugin", "add", f"{PLUGIN_NAME}@{PLUGIN_NAME}"], env=env)
        result = subprocess.run(
            [codex, "plugin", "list"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        if PLUGIN_NAME not in result.stdout:
            raise SystemExit(f"Codex plugin list missing path-to-academia:\n{result.stdout}")


def validate_workspace() -> None:
    with tempfile.TemporaryDirectory(prefix="path-to-academia-check-") as tmp:
        workspace = Path(tmp) / "workspace"
        run([sys.executable, "scripts/init_workspace.py", str(workspace), "--example", "ml-bio", "--force"])
        run([sys.executable, "scripts/qa_workspace.py", str(workspace)])
        context = run_json([sys.executable, "scripts/workspace_context.py", str(workspace)])
        if context.get("quality", {}).get("row_count") != 3:
            raise SystemExit("workspace context did not report the example rows")
        run(
            [
                sys.executable,
                "scripts/export_wrapped_xlsx.py",
                str(workspace / "tables" / "entities_final.csv"),
                str(workspace / "tables" / "entities_final_wrapped.xlsx"),
            ]
        )


def validate_plugin_bundle_runtime() -> None:
    try:
        with tempfile.TemporaryDirectory(prefix="path-to-academia-bundle-check-") as tmp:
            workspace = Path(tmp) / "workspace"
            run(
                [
                    sys.executable,
                    "scripts/init_workspace.py",
                    str(workspace),
                    "--example",
                    "ml-bio",
                    "--force",
                ],
                cwd=PLUGIN_BUNDLE,
            )
            run([sys.executable, "scripts/qa_workspace.py", str(workspace)], cwd=PLUGIN_BUNDLE)
            context = run_json([sys.executable, "scripts/workspace_context.py", str(workspace)], cwd=PLUGIN_BUNDLE)
            if context.get("quality", {}).get("row_count") != 3:
                raise SystemExit("plugin bundle context did not report the example rows")
            outdir = Path(tmp) / "dist"
            run([sys.executable, "-m", "build", "--outdir", str(outdir)], cwd=PLUGIN_BUNDLE)
            version = project_version()
            wheel = outdir / f"path_to_academia-{version}-py3-none-any.whl"
            if not wheel.exists():
                raise SystemExit(f"plugin bundle did not build expected wheel: {wheel}")
    finally:
        clean_plugin_bundle_generated()


def build_and_smoke_install() -> None:
    version = project_version()
    with tempfile.TemporaryDirectory(prefix="path-to-academia-build-") as tmp:
        outdir = Path(tmp) / "dist"
        run([sys.executable, "-m", "build", "--outdir", str(outdir)])
        sdist = outdir / f"path_to_academia-{version}.tar.gz"
        wheel = outdir / f"path_to_academia-{version}-py3-none-any.whl"
        required_sdist = {
            f"path_to_academia-{version}/.agents/plugins/marketplace.json",
            f"path_to_academia-{version}/.codex-plugin/plugin.json",
            f"path_to_academia-{version}/.claude-plugin/plugin.json",
            f"path_to_academia-{version}/.claude-plugin/marketplace.json",
            f"path_to_academia-{version}/.github/workflows/ci.yml",
            f"path_to_academia-{version}/.github/pull_request_template.md",
            f"path_to_academia-{version}/AGENTS.md",
            f"path_to_academia-{version}/CODE_OF_CONDUCT.md",
            f"path_to_academia-{version}/CITATION.cff",
            f"path_to_academia-{version}/CONTRIBUTING.md",
            f"path_to_academia-{version}/SECURITY.md",
            f"path_to_academia-{version}/install-claude.sh",
            f"path_to_academia-{version}/docs/architecture.md",
            f"path_to_academia-{version}/docs/privacy.md",
            f"path_to_academia-{version}/skills/path-to-academia/SKILL.md",
            f"path_to_academia-{version}/plugins/path-to-academia/.codex-plugin/plugin.json",
            f"path_to_academia-{version}/plugins/path-to-academia/.claude-plugin/plugin.json",
            f"path_to_academia-{version}/plugins/path-to-academia/AGENTS.md",
            f"path_to_academia-{version}/plugins/path-to-academia/skills/path-to-academia/SKILL.md",
            f"path_to_academia-{version}/plugins/path-to-academia/scripts/init_workspace.py",
            f"path_to_academia-{version}/plugins/path-to-academia/src/path_to_academia/cli.py",
        }
        with tarfile.open(sdist) as archive:
            names = set(archive.getnames())
        missing_sdist = sorted(required_sdist - names)
        if missing_sdist:
            raise SystemExit(f"missing sdist files: {missing_sdist}")
        generated_sdist = sorted(
            name
            for name in names
            if "/plugins/path-to-academia/" in name
            and ("__pycache__" in name or name.endswith(".pyc") or ".egg-info/" in name or name.endswith(".egg-info"))
        )
        if generated_sdist:
            raise SystemExit("generated plugin bundle files leaked into sdist:\n" + "\n".join(generated_sdist))
        required_wheel = {
            "path_to_academia/webui/static/index.html",
            "path_to_academia/webui/static/app.js",
            "path_to_academia/webui/static/styles.css",
            "path_to_academia/webui/static/i18n.json",
            f"path_to_academia-{version}.dist-info/entry_points.txt",
        }
        with ZipFile(wheel) as archive:
            wheel_names = set(archive.namelist())
        missing_wheel = sorted(required_wheel - wheel_names)
        if missing_wheel:
            raise SystemExit(f"missing wheel files: {missing_wheel}")
        venv_dir = Path(tmp) / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        bin_dir = "Scripts" if os.name == "nt" else "bin"
        python = venv_dir / bin_dir / "python"
        cli = venv_dir / bin_dir / "path-to-academia"
        run([str(python), "-m", "pip", "install", "--quiet", str(wheel)])
        run([str(cli), "--help"])
        smoke_workspace = Path(tmp) / "smoke-workspace"
        run([str(cli), "init", str(smoke_workspace), "--example", "empty"])
        context = run_json([str(cli), "context", str(smoke_workspace)])
        if context.get("quality", {}).get("row_count") != 0:
            raise SystemExit("wheel smoke context did not report an empty workspace")
        run([str(cli), "qa", str(smoke_workspace)])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run path to academia release checks.")
    parser.add_argument("--skip-codex", action="store_true", help="Skip local Codex plugin/skill validators.")
    parser.add_argument("--skip-claude", action="store_true", help="Skip local Claude Code plugin validator.")
    parser.add_argument("--strict-codex", action="store_true", help="Fail if Codex validators are unavailable.")
    parser.add_argument("--strict-claude", action="store_true", help="Fail if Claude Code validator is unavailable.")
    parser.add_argument("--skip-build", action="store_true", help="Skip package build and wheel install smoke test.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        clean_generated()
        validate_versions()
        validate_plugin_bundle()
        validate_i18n()
        validate_residue()
        run([sys.executable, "-m", "pytest"])
        run([sys.executable, "-m", "py_compile", *python_files()])
        validate_workspace()
        validate_codex_install_script()
        validate_codex_marketplace_cli(skip_codex=args.skip_codex, strict_codex=args.strict_codex)
        validate_claude_install_script()
        validate_codex(skip_codex=args.skip_codex, strict_codex=args.strict_codex)
        validate_claude(skip_claude=args.skip_claude, strict_claude=args.strict_claude)
        if not args.skip_build:
            validate_plugin_bundle_runtime()
            build_and_smoke_install()
        print("release check passed")
        return 0
    finally:
        clean_generated()


if __name__ == "__main__":
    raise SystemExit(main())
