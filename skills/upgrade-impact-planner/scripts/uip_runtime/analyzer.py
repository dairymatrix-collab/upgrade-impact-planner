from __future__ import annotations
from pathlib import Path
from .discovery import discover_dependencies, repository_fingerprint
from .evidence import load_evidence
from .models import AnalysisReport, ImpactFinding
from .scanner import scan_symbols


def _target_match(name: str, target: str) -> bool:
    return name.lower().replace("_", "-") == target.lower().replace("_", "-") or name.lower().endswith("/" + target.lower())


def analyze(root: Path, target: str, to_version: str | None=None, evidence_path: Path | None=None) -> AnalysisReport:
    dependencies=discover_dependencies(root)
    selected=[d for d in dependencies if _target_match(d.name, target)]
    changes, evidence_status, warnings=load_evidence(evidence_path)
    findings=[]
    for change in changes:
        matches=scan_symbols(root, change.symbols)
        status="confirmed" if matches else "evidence-only"
        confidence=min(0.99, change.confidence + (0.08 if matches else 0))
        findings.append(ImpactFinding(change.change_id, change.category, change.summary, change.migration, change.source, round(confidence, 2), matches, status))
    blockers=[]
    if not selected: blockers.append(f"Target {target!r} was not found in a supported manifest.")
    if evidence_status != "complete": blockers.append("Official evidence coverage is not complete; do not treat this report as a clean upgrade.")
    plan=[
        {"phase":"preparation","actions":["Review official release notes and confirm the target version.", "Create a clean branch and record the current lockfile/state."]},
        {"phase":"code migration","actions":[f"Address {sum(1 for f in findings if f.matches)} confirmed source impact finding(s).", "Review evidence-only changes manually before editing."]},
        {"phase":"validation","actions":["Run the repository's existing unit, integration, lint, typecheck, and build commands.", "Run focused tests for every confirmed finding."]},
        {"phase":"cleanup","actions":["Search for deprecated symbols again.", "Review generated files, documentation, and lockfile changes."]},
    ]
    rollback=["Keep the pre-upgrade commit and lockfile available.", "Revert the dependency manifest and lockfile together if validation fails.", "Do not publish or deploy until the focused and full test suites pass."]
    if evidence_status == "missing": warnings.append("Add an official release note, migration guide, or structured evidence file for stronger conclusions.")
    target_data={"name":target,"from":selected[0].current_version if selected else None,"to":to_version,"ecosystems":sorted({d.ecosystem for d in selected}),"manifest_count":len(selected)}
    return AnalysisReport(1,"0.1.0",str(root),target_data,{"repository":repository_fingerprint(root),"official_evidence":evidence_status,"source_scan":"complete"},selected,findings,blockers,plan,rollback,warnings)
