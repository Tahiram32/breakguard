"""AST-level analysis for downstream breakage detection in Python files.

Uses Python's built-in `ast` module to deeply understand code changes and
detect when public symbols are removed or their signatures change.
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set, Dict

from downstream_breakage_radar.scanner import Finding


@dataclass
class FuncDef:
    name: str
    args: list[str]
    kwonlyargs: list[str]
    defaults_count: int
    kw_defaults_count: int


def _get_public_functions(tree: ast.AST) -> dict[str, FuncDef]:
    """Extract public functions and their signatures from an AST."""
    funcs = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                args = [arg.arg for arg in node.args.args]
                kwonlyargs = [arg.arg for arg in node.args.kwonlyargs]
                defaults_count = len(node.args.defaults)
                # kw_defaults can contain None, so we count non-None
                kw_defaults_count = sum(1 for d in node.args.kw_defaults if d is not None)
                
                funcs[node.name] = FuncDef(
                    name=node.name,
                    args=args,
                    kwonlyargs=kwonlyargs,
                    defaults_count=defaults_count,
                    kw_defaults_count=kw_defaults_count,
                )
    return funcs


def _get_public_classes(tree: ast.AST) -> set[str]:
    """Extract public classes from an AST."""
    classes = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                classes.add(node.name)
    return classes


def _get_file_content_at_ref(repo_path: Path, ref: str, file_path: str) -> str | None:
    """Get the content of a file at a specific git ref."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_path), "show", f"{ref}:{file_path}"],
            check=True,
            text=True,
            capture_output=True,
        )
        return completed.stdout
    except subprocess.CalledProcessError:
        return None


def analyze_python_ast(repo_path: Path, changed_files: Iterable[str], base_ref: str) -> list[Finding]:
    """Parse Python ASTs to detect removed symbols and signature changes."""
    findings: list[Finding] = []

    for path in changed_files:
        if not path.endswith(".py"):
            continue

        # Get the old content
        old_content = _get_file_content_at_ref(repo_path, base_ref, path)
        if not old_content:
            continue  # File was likely added, no breakage possible

        # Get the new content
        new_path = repo_path / path
        if not new_path.exists():
            continue  # File deleted; diff_analyzer handles this

        try:
            new_content = new_path.read_text(encoding="utf-8")
        except Exception:
            continue

        try:
            old_tree = ast.parse(old_content)
            new_tree = ast.parse(new_content)
        except SyntaxError:
            continue  # Skip if there's a syntax error (e.g. invalid Python code)

        old_funcs = _get_public_functions(old_tree)
        new_funcs = _get_public_functions(new_tree)

        old_classes = _get_public_classes(old_tree)
        new_classes = _get_public_classes(new_tree)

        # 1. Check for removed classes
        for cls in old_classes:
            if cls not in new_classes:
                findings.append(
                    Finding(
                        severity="high",
                        path=path,
                        message=f"Removed public class: {cls}",
                        migration_note=f"The class '{cls}' was removed from {path}. Consumers will break.",
                    )
                )

        # 2. Check for removed functions or signature changes
        for name, old_func in old_funcs.items():
            if name not in new_funcs:
                findings.append(
                    Finding(
                        severity="high",
                        path=path,
                        message=f"Removed public function: {name}",
                        migration_note=f"The function '{name}' was removed from {path}. Consumers will break.",
                    )
                )
            else:
                new_func = new_funcs[name]
                
                # Check if required arguments increased (or defaults removed)
                old_req_args = len(old_func.args) - old_func.defaults_count
                new_req_args = len(new_func.args) - new_func.defaults_count
                
                if new_req_args > old_req_args:
                    findings.append(
                        Finding(
                            severity="high",
                            path=path,
                            message=f"Function signature changed: {name}",
                            migration_note=f"The function '{name}' in {path} now requires more positional arguments.",
                        )
                    )
                    continue

                # Check if named arguments were removed
                old_all_args = set(old_func.args + old_func.kwonlyargs)
                new_all_args = set(new_func.args + new_func.kwonlyargs)
                missing_args = old_all_args - new_all_args
                
                if missing_args:
                    findings.append(
                        Finding(
                            severity="high",
                            path=path,
                            message=f"Function signature changed: {name}",
                            migration_note=f"The function '{name}' in {path} removed arguments: {', '.join(missing_args)}.",
                        )
                    )

    return findings
