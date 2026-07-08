<div align="center">

# 📡 Downstream Breakage Radar

**Detect breaking changes before they break your users.**

[![Breakage Radar](https://github.com/Tahiram32/downstream-breakage-radar/actions/workflows/scan.yml/badge.svg)](https://github.com/Tahiram32/downstream-breakage-radar/actions/workflows/scan.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/downloads/)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-ea4aaa.svg)](https://github.com/sponsors/Tahiram32)

A GitHub Action and CLI that scans your pull requests for changes likely to break downstream consumers — and generates plain-English migration notes so nobody gets surprised on release day.

</div>

---

## Why?

Every library maintainer has lived this nightmare: you merge a PR, cut a release, and within hours your issue tracker fills up with reports from projects that depended on the function you renamed, the config key you removed, or the default you changed.

**Downstream Breakage Radar** catches those risks *before* they reach `main`. It diffs your branch against a base ref, identifies changes that touch public API surfaces and release-critical files, and tells you — in plain English — what downstream users will need to do.

No external dependencies. No complex setup. Just add it to your workflow and ship with confidence.

## ✨ Features

- 🔍 **Automatic surface detection** — flags changes to `src/`, `lib/`, `api/`, `schemas/`, `proto/`, OpenAPI specs, and more
- 📦 **Package manifest awareness** — catches edits to `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, etc.
- 📝 **Migration notes** — every finding includes a human-readable note explaining what to review
- 🎯 **Risk scoring** — summarizes overall risk level (`none` / `low` / `medium` / `high`) at a glance
- 🚨 **Dependency Mismatch Detection** — automatically flags missing imports (critical) or declared-but-unused packages in manifests
- 📊 **Custom SVG Badges** — generates a clean `breakage-radar-badge.svg` representing the overall risk level for your PRs
- 🖥️ **Dual mode** — runs as a GitHub Action in CI *or* locally as a CLI
- 📊 **Multiple output formats** — plain text, JSON, markdown PR comments, or GitHub Actions annotations
- 🪶 **Zero dependencies** — pure Python, nothing to install beyond the standard library

## 🚀 Quick Start

### As a GitHub Action (recommended)

Add this to `.github/workflows/breakage-radar.yml`:

```yaml
name: Breakage Radar

on:
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Scan for breaking changes
        uses: Tahiram32/downstream-breakage-radar@main
        with:
          base-ref: origin/main
          format: markdown
          fail-on: high
```

### As a CLI

```bash
# Install from source
pip install git+https://github.com/Tahiram32/downstream-breakage-radar.git

# Scan the current repo against origin/main
breakage-radar --repo . --base origin/main

# Get JSON output for CI tooling
breakage-radar --repo . --base origin/main --format json
```

Or run directly as a module:

```bash
python -m downstream_breakage_radar.cli --repo . --base origin/main
```

## 📋 Example Output

### Text format

```
Risk level: medium
Changed files: 4
Findings: 3

- [medium] src/api/client.py: Change touches a likely public surface or release-critical file.
  Migration note: Review for API compatibility, config drift, and release notes before merging.

- [low] src/api/client.py: Source code change may affect downstream consumers.
  Migration note: Check for renamed symbols, changed defaults, and behavior shifts.

- [medium] pyproject.toml: Change touches a likely public surface or release-critical file.
  Migration note: Review for API compatibility, config drift, and release notes before merging.
```

### JSON format

```json
{
  "change_count": 4,
  "changed_files": [
    "src/api/client.py",
    "pyproject.toml",
    "docs/guide.md",
    "tests/test_client.py"
  ],
  "finding_count": 3,
  "findings": [
    {
      "message": "Change touches a likely public surface or release-critical file.",
      "migration_note": "Review for API compatibility, config drift, and release notes before merging.",
      "path": "src/api/client.py",
      "severity": "medium"
    }
  ],
  "risk_level": "medium"
}
```

## ⚙️ Configuration

| Input | Default | Description |
|-------|---------|-------------|
| `--repo` | `.` | Path to the Git repository to scan |
| `--base` | `origin/main` | Base ref to diff against (branch, tag, or commit SHA) |
| `--format` | `text` | Output format: `text` for human-readable, `json` for machine-readable |
| `--fail-on` | `high` | The risk level at which to exit with code 1 |
| `--draft-release` | `false` | Automatically draft a GitHub release using the `gh` CLI |

### Ignore Files

Create a `.breakageignore` file in the root of your repository to specify glob patterns for paths you want the scanner to completely ignore (e.g. `src/internal_scripts/*` or `*_test.py`).

### GitHub Action inputs

When using as a GitHub Action, pass configuration via the `with` keyword. The action requires `fetch-depth: 0` on checkout so the full git history is available for diffing.

## 🔬 How It Works

1. **Diff** — runs `git diff --name-only <base-ref>...HEAD` to get the list of changed files
2. **Classify** — checks each path against known risky patterns:
   - **Path markers**: `src/`, `lib/`, `app/`, `api/`, `public/`, `include/`, `internal/`, `pkg/`, `schemas/`, `proto/`, `openapi`
   - **Package manifests**: `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, and more
   - **Source extensions**: `.py`, `.ts`, `.js`, `.go`, `.rs`, `.java`, `.kt`, `.cs`
3. **Score** — assigns severity (`low` for source changes, `medium` for public surface / manifest changes)
4. **Report** — generates a summary with per-file findings and plain-English migration notes

## 🗺️ Roadmap

- [x] Diff-aware API surface detection (AST-level analysis)
- [x] Language-specific adapters for smarter risk scoring (Python, Go, JS/TS)
- [x] Automated release-note drafting
- [x] Downstream repository impact hints
- [x] `fail-on` threshold to block PRs above a risk level
- [x] Native GitHub inline annotations (Workflow Commands)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up the dev environment, running tests, and submitting pull requests.

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## ❤️ Sponsor This Project

Downstream Breakage Radar is free, open-source software maintained in spare time. Sponsorship directly funds:

- 🛠️ **New features** from the roadmap (AST analysis, language adapters, SARIF output)
- 🐛 **Bug fixes and maintenance** to keep the tool reliable
- 📖 **Documentation and examples** to help more teams adopt it
- 🌍 **Community support** — answering issues, reviewing PRs, and growing the ecosystem

If this tool saves your team from a breaking release, consider supporting its development:

**[→ Sponsor @Tahiram32 on GitHub](https://github.com/sponsors/Tahiram32)**

Every contribution — no matter the size — helps keep this project alive and moving forward. Thank you! 🙏
