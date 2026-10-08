#!/usr/bin/env python3
"""Generate a bounded Markdown inventory for repository architecture discovery."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

IGNORED_DIRS = {".git", ".idea", ".vscode", ".venv", "venv", "node_modules", "dist", "build", "target", "coverage", ".next", ".nuxt", "vendor", "__pycache__"}
MANIFESTS = {"package.json", "pnpm-workspace.yaml", "pyproject.toml", "requirements.txt", "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "Cargo.toml", "go.mod", "Gemfile", "composer.json", "Makefile", "docker-compose.yml", "docker-compose.yaml", "Dockerfile"}
ENTRY_NAMES = {"main.py", "app.py", "manage.py", "server.py", "main.ts", "main.js", "index.ts", "index.js", "Program.cs", "Application.java", "main.go"}
CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".kts", ".go", ".rs", ".rb", ".php", ".cs", ".cpp", ".cc", ".c", ".h", ".hpp", ".swift", ".scala", ".sql", ".proto", ".graphql"}


def scan(root: Path, max_files: int) -> dict[str, object]:
    files: list[Path] = []
    manifests: list[Path] = []
    entries: list[Path] = []
    configs: list[Path] = []
    tests: list[Path] = []
    suffixes: Counter[str] = Counter()
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts) or not path.is_file():
            continue
        files.append(path)
        if path.name in MANIFESTS:
            manifests.append(rel)
        if path.name in ENTRY_NAMES or path.name.endswith("Application.java"):
            entries.append(rel)
        if path.suffix.lower() in {".yml", ".yaml", ".toml", ".properties", ".json"}:
            configs.append(rel)
        lowered = str(rel).lower()
        if "test" in rel.parts or "/test" in lowered or path.name.startswith("test_") or ".test." in path.name:
            tests.append(rel)
        if path.suffix.lower() in CODE_SUFFIXES:
            suffixes[path.suffix.lower()] += 1
        if len(files) >= max_files:
            break
    top_dirs = sorted({p.relative_to(root).parts[0] for p in files if len(p.relative_to(root).parts) > 1})
    return {"files": files, "manifests": sorted(manifests), "entries": sorted(entries), "configs": sorted(configs), "tests": sorted(tests), "suffixes": suffixes, "top_dirs": top_dirs, "truncated": len(files) >= max_files}


def bullet(paths: list[Path], limit: int = 40) -> str:
    if not paths:
        return "- 未发现"
    lines = [f"- `{path}`" for path in paths[:limit]]
    if len(paths) > limit:
        lines.append(f"- …另有 {len(paths) - limit} 项")
    return "\n".join(lines)


def render(root: Path, data: dict[str, object], max_files: int) -> str:
    suffixes = data["suffixes"]
    assert isinstance(suffixes, Counter)
    rows = "\n".join(f"| `{suffix}` | {count} |" for suffix, count in suffixes.most_common(20)) or "| 未识别 | 0 |"
    truncated = "是" if data["truncated"] else "否"
    return f"""# Repository Inventory

- Root: `{root.resolve()}`
- Scanned files: {len(data['files'])}
- Scan limit: {max_files}
- Truncated: {truncated}

> 本清单用于导航，不构成架构结论。入口、模块边界和运行链路仍需源码验证。

## Top-level directories
{bullet([Path(p) for p in data['top_dirs']])}

## Manifests and build files
{bullet(data['manifests'])}

## Candidate entrypoints
{bullet(data['entries'])}

## Configuration files
{bullet(data['configs'])}

## Test files
{bullet(data['tests'])}

## Code suffixes
| Suffix | Count |
|---|---:|
{rows}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-files", type=int, default=20000)
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    if args.max_files < 1:
        parser.error("--max-files must be positive")
    text = render(root, scan(root, args.max_files), args.max_files)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
