---
name: upgrade-impact-planner
description: Evidence-first dependency upgrade, framework migration, runtime change, breaking-change, and deprecated-API impact analysis. Use when planning a package or API upgrade, reviewing a Dependabot major update, diagnosing migration risk, mapping release-note changes to repository files, or creating a safe migration and rollback plan.
license: MIT
---

# Upgrade Impact Planner

Use the bundled `uip` CLI as the deterministic core. This skill is report-only by default: it does not install packages, edit source, commit, push, or deploy.

## Fast path

From the repository root, install the full toolkit when possible:

```bash
python -m pip install -e .
uip scan . --json .uip/dependencies.json
uip analyze . --target requests --to 3.0.0 \
  --evidence vendor/requests-3-migration.md \
  --json .uip/impact.json --markdown .uip/impact.md
```

When only this skill directory is available, run its bundled physical runtime directly:

```bash
python skills/upgrade-impact-planner/scripts/uip.py scan .
python skills/upgrade-impact-planner/scripts/uip.py analyze . --target requests --to 3.0.0 --evidence migration.md
```

If the repository has no official release notes or migration guide, omit `--evidence`; the report must show `official_evidence: missing` and must not call the upgrade safe.

## Ordered workflow

1. Identify the repository, target dependency/framework/runtime/API, current version, requested target, package manager, lockfile, and existing test commands.
2. Run `uip scan REPO` and inspect supported manifests. Do not infer a dependency from a README alone.
3. Collect authoritative evidence from the vendor's official release notes, migration guide, deprecation page, compatibility matrix, or changelog. Treat issue comments and third-party posts as context, not proof.
4. Run `uip analyze` with the evidence file. Structured JSON evidence is preferred for automation; Markdown release notes are supported for human-provided sources.
5. Review every finding. `confirmed` means an evidence symbol matched repository source; `evidence-only` means the change is real evidence but no direct source match was found. Neither status proves runtime correctness.
6. Check blockers, missing evidence, peer/runtime requirements, generated/vendor files, lockfile effects, and test coverage. Missing evidence is a blocker, not a clean result.
7. Present the Markdown report for approval. Only after explicit approval may a separate implementation workflow edit files; re-run the analyzer and tests afterward.

## Evidence rules

Never invent a migration step, version, compatibility claim, or affected file. Preserve the evidence source in each finding. If the official source is unreachable or incomplete, use `partial` or `blocked`. Keep uncertain possibilities in warnings. Use `uip redact` before sharing logs or reports that may contain tokens.

## Supported discovery

The coded engine detects direct dependencies in `package.json`, `pyproject.toml`, common `requirements*.txt` files, `go.mod`, `Cargo.toml`, and Dockerfiles. It scans source files while skipping Git metadata, virtual environments, vendored packages, build output, node_modules, lockfiles, binary files, and common generated files. It is intentionally conservative: unsupported package managers require a manual evidence note.

## Output contract

The JSON packet contains the target, detected dependency, evidence coverage, source matches with file and line references, confidence, blockers, phased preparation/code-migration/validation/cleanup plan, rollback steps, and warnings. The Markdown report is for maintainers; JSON is for CI or downstream automation. Both state that no repository mutation occurred.

## Safety boundary

Do not run package installation or deployment as part of analysis. Do not use a passing test as proof that an upgrade is safe. Do not hide an absent migration guide. Redact credentials before processing shared logs. Never turn a report into an automatic dependency bump without a human-selected target and approval.
