from __future__ import annotations
import json
from .models import AnalysisReport


def render_json(report: AnalysisReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"


def render_markdown(report: AnalysisReport) -> str:
    lines=[f"# Upgrade Impact Report: `{report.target['name']}`", "", "## Verdict", "", f"- Current version: `{report.target.get('from') or 'not detected'}`", f"- Target version: `{report.target.get('to') or 'not specified'}`", f"- Official evidence: **{report.coverage['official_evidence']}**", f"- Source scan: **{report.coverage['source_scan']}**", "- Execution: **report-only; no files changed**", ""]
    if report.blockers:
        lines += ["## Blockers", ""] + [f"- {x}" for x in report.blockers] + [""]
    lines += ["## Detected dependency", ""]
    if report.dependencies:
        lines += ["| Ecosystem | Dependency | Current | Manifest |", "|---|---|---|---|"] + [f"| {d.ecosystem} | `{d.name}` | `{d.current_version or 'unknown'}` | `{d.manifest}` |" for d in report.dependencies] + [""]
    else: lines += ["No matching dependency was detected in supported manifests.", ""]
    lines += ["## Impact findings", ""]
    if not report.findings: lines.append("No evidence changes were parsed. This is not evidence that the upgrade is safe.")
    for finding in report.findings:
        lines += [f"### {finding.category}: {finding.summary}", "", f"- Status: **{finding.status}**", f"- Confidence: **{finding.confidence:.2f}**", f"- Migration: {finding.migration}", f"- Evidence: `{finding.source}`"]
        if finding.matches:
            lines += ["- Affected locations:"] + [f"  - `{m.path}:{m.start_line}` — `{m.matched_symbol}` — {m.excerpt}" for m in finding.matches]
        else: lines.append("- Affected locations: no direct source match found; manual review required.")
        lines.append("")
    lines += ["## Migration plan", ""]
    for phase in report.plan:
        lines.append(f"### {phase['phase']}")
        lines += [f"- {action}" for action in phase["actions"]] + [""]
    lines += ["## Rollback", ""] + [f"- {x}" for x in report.rollback] + [""]
    if report.warnings: lines += ["## Warnings", ""] + [f"- {x}" for x in report.warnings] + [""]
    lines += ["## Safety boundary", "", "This report is evidence-first and read-only. It does not install packages, edit source files, commit, push, close issues, or deploy.", ""]
    return "\n".join(lines)
