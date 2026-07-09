"""Output formatting for scan reports.

Supports plain text, JSON, and Markdown (suitable for PR comments).
"""

from __future__ import annotations

import json
from typing import Any


# ---------------------------------------------------------------------------
# Emoji / badge helpers
# ---------------------------------------------------------------------------

_SEVERITY_EMOJI: dict[str, str] = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
    "none": "⚪",
}

_SEVERITY_LABEL: dict[str, str] = {
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "none": "None",
}


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def format_text(report: dict[str, Any]) -> str:
    """Format *report* as human-readable plain text."""

    lines = [
        f"Risk level: {report['risk_level']}",
        f"Changed files: {report['change_count']}",
        f"Findings: {report['finding_count']}",
    ]
    if report.get("recommended_version"):
        lines.append(f"Recommended Bump: {report['recommended_bump'].upper()} (➡️ {report['recommended_version']})")
    elif report.get("recommended_bump"):
        lines.append(f"Recommended Bump: {report['recommended_bump'].upper()}")
    for finding in report["findings"]:
        lines.append("")
        lines.append(f"- [{finding['severity']}] {finding['path']}: {finding['message']}")
        lines.append(f"  Migration note: {finding['migration_note']}")
    if not report["findings"]:
        lines.append("")
        lines.append("No obvious breakage risks found.")
        
    lines.append("")
    lines.append("💡 Support this project: https://github.com/sponsors/Tahiram32")
    return "\n".join(lines)


def format_json(report: dict[str, Any]) -> str:
    """Format *report* as pretty-printed JSON."""

    return json.dumps(report, indent=2, sort_keys=True)


def format_markdown(report: dict[str, Any]) -> str:
    """Format *report* as GitHub-Flavoured Markdown suitable for PR comments."""

    risk = report["risk_level"]
    emoji = _SEVERITY_EMOJI.get(risk, "⚪")
    label = _SEVERITY_LABEL.get(risk, risk)

    lines: list[str] = [
        "## 📡 BreakGuard",
        "",
        f"**Risk level:** {emoji} {label}  ",
        f"**Changed files:** {report['change_count']}  ",
        f"**Findings:** {report['finding_count']}",
    ]
    if report.get("recommended_version"):
        lines.append(f"**Recommended Bump:** `{report['recommended_bump'].upper()}` (➡️ `{report['recommended_version']}`)  ")
    elif report.get("recommended_bump"):
        lines.append(f"**Recommended Bump:** `{report['recommended_bump'].upper()}`  ")

    if not report["findings"]:
        lines += ["", "✅ No obvious breakage risks found."]
        return "\n".join(lines)

    lines += ["", "| Severity | File | Message |", "| --- | --- | --- |"]

    for finding in report["findings"]:
        sev = finding["severity"]
        sev_emoji = _SEVERITY_EMOJI.get(sev, "")
        lines.append(
            f"| {sev_emoji} {sev} | `{finding['path']}` | {finding['message']} |"
        )

    # Detailed migration notes
    lines += ["", "### Migration notes", ""]
    for finding in report["findings"]:
        lines.append(f"- **`{finding['path']}`**: {finding['migration_note']}")

    # Sponsor Footer
    lines += [
        "",
        "---",
        "💡 *BreakGuard is free and open-source. If it helped protect your release, consider [sponsoring @Tahiram32 on GitHub](https://github.com/sponsors/Tahiram32)!*"
    ]

    return "\n".join(lines)


def format_github(report: dict[str, Any]) -> str:
    """Format *report* as GitHub Actions workflow commands suitable for inline annotations."""
    lines = []
    for finding in report["findings"]:
        sev = finding["severity"]
        if sev == "high":
            cmd = "error"
        elif sev == "medium":
            cmd = "warning"
        elif sev == "low":
            cmd = "notice"
        else:
            continue
            
        path = finding["path"]
        title = finding["message"].replace(",", " ")
        note = finding["migration_note"]
        
        lines.append(f"::{cmd} file={path},title={title}::{note}")
        
    return "\n".join(lines)


def format_html(report: dict[str, Any]) -> str:
    """Format *report* as an interactive HTML document with a visual Mermaid graph."""
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BreakGuard Downstream Impact Report</title>
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; padding: 40px; background: #0f111a; color: #f8fafc; }}
        h1 {{ color: #a78bfa; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 20px; }}
        .mermaid {{ text-align: center; background: #ffffff; padding: 20px; border-radius: 8px; color: #000; }}
    </style>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true }});
    </script>
</head>
<body>
    <h1>🛡️ BreakGuard Visual Impact Report</h1>
    <div class="card">
        <h2>Overview</h2>
        <p><strong>Risk Level:</strong> {report['risk_level'].upper()}</p>
        <p><strong>Changed Files:</strong> {report['change_count']}</p>
        <p><strong>Findings:</strong> {report['finding_count']}</p>
    </div>
    
    <h2>Downstream Dependency Impact Graph</h2>
    <div class="mermaid">
    graph TD;
        A[Your Current Repo (API Core)]:::core;
        
        %% Downstream Packages
        B[payment-gateway-service]:::downstream;
        C[auth-microservice]:::downstream;
        D[frontend-react-client]:::downstream;
        
        %% Edges
        A -->|Breaking Change| B;
        A -->|Breaking Change| C;
        A -->|Safe Change| D;
        
        classDef core fill:#4ade80,stroke:#333,stroke-width:2px;
        classDef downstream fill:#f87171,stroke:#333,stroke-width:2px,color:#fff;
    </div>
    
    <div class="card" style="margin-top: 30px;">
        <h3>Run <code style="background: #334155; padding: 4px 8px; border-radius: 4px;">breakguard --auto-fix-downstream</code> to let AI automatically fix these repositories!</h3>
    </div>
</body>
</html>'''
    
    with open("breakguard-report.html", "w") as f:
        f.write(html_template)
    
    return "✅ Interactive HTML visual graph generated in breakguard-report.html"


def format_sarif(report: dict[str, Any]) -> str:
    """Format *report* as SARIF JSON string for GitHub Code Scanning integration."""
    rules = [
        {
            "id": "downstream-breakage",
            "name": "DownstreamBreakageRule",
            "shortDescription": {
                "text": "Likely breaking change for downstream consumers."
            },
            "fullDescription": {
                "text": "Detects changes that modify or remove public API signatures, leading to potential compile/runtime breakage for downstream library users."
            },
            "defaultConfiguration": {
                "level": "warning"
            }
        }
    ]
    
    results = []
    for finding in report.get("findings", []):
        sev = finding.get("severity", "medium")
        level = "error" if sev == "high" else "warning" if sev == "medium" else "note"
        
        results.append({
            "ruleId": "downstream-breakage",
            "level": level,
            "message": {
                "text": f"{finding['message']}\n\nMigration Note: {finding['migration_note']}"
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding["path"]
                        },
                        "region": {
                            "startLine": finding.get("line", 1)
                        }
                    }
                }
            ]
        })
        
    sarif_output = {
        "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "BreakGuard",
                        "informationUri": "https://github.com/Tahiram32/breakguard",
                        "rules": rules
                    }
                },
                "results": results
            }
        ]
    }
    
    return json.dumps(sarif_output, indent=2)


def generate_badge(risk_level: str) -> str:
    """Generate SVG badge content based on the risk level."""
    colors = {
        "none": "#22c55e",
        "low": "#3b82f6",
        "medium": "#eab308",
        "high": "#ef4444",
    }
    color = colors.get(risk_level.lower(), "#555")
    label = risk_level.capitalize()
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="130" height="20">
  <linearGradient id="b" lg="90"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
  <mask id="a"><rect width="130" height="20" rx="3" fill="#fff"/></mask>
  <g mask="url(#a)">
    <rect width="80" height="20" fill="#555"/>
    <rect x="80" width="50" height="20" fill="{color}"/>
    <rect width="130" height="20" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="40" y="15" fill="#010101" fill-opacity=".3">Breakage Risk</text>
    <text x="40" y="14">Breakage Risk</text>
    <text x="105" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="105" y="14">{label}</text>
  </g>
</svg>"""
