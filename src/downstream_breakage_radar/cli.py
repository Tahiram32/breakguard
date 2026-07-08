from __future__ import annotations

import argparse
import sys
from pathlib import Path

from downstream_breakage_radar import ast_analyzer, diff_analyzer, reporter, scanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect likely downstream breakage before release.")
    parser.add_argument("--repo", default=".", help="Path to the repository to scan.")
    parser.add_argument("--base", default="origin/main", help="Base ref for git diff.")
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format."
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "low", "medium", "high"),
        default="high",
        help="Fail (exit code 1) if overall risk level is >= this severity.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    repo_path = Path(args.repo).resolve()
    
    # Run the core detection
    changed_files = scanner.git_changed_files(repo_path, args.base)
    deleted_files = scanner.git_deleted_files(repo_path, args.base)
    diff_text = scanner.git_diff(repo_path, args.base)

    findings = scanner.detect_risk(changed_files)
    findings.extend(diff_analyzer.analyze_diff(diff_text, deleted_files))
    findings.extend(ast_analyzer.analyze_python_ast(repo_path, changed_files, args.base))

    report = scanner.summarize(findings, changed_files)

    # Output
    if args.format == "json":
        print(reporter.format_json(report))
    elif args.format == "markdown":
        print(reporter.format_markdown(report))
    else:
        print(reporter.format_text(report))

    # Exit code based on fail-on
    if args.fail_on != "none":
        risk = report["risk_level"]
        order = scanner.SEVERITY_ORDER
        if order.get(risk, 0) >= order.get(args.fail_on, 0):
            print(f"\nError: Overall risk level '{risk}' exceeds threshold '{args.fail_on}'.", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
