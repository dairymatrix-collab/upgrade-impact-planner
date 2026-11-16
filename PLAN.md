# Upgrade Impact Planner — Build Plan

## Product contract

This is a runnable, read-only-first toolkit. Given a repository, target dependency/API, target version, and optional official release notes, it produces a machine-readable impact packet and a human-readable migration report. It must never claim a breaking change without evidence or a repository match, and it must never edit, install, commit, or push by default.

## Milestones

1. **Core discovery:** detect common manifests and extract direct dependency versions.
2. **Evidence parser:** parse structured JSON and Markdown release notes into normalized change records.
3. **Impact scanner:** map change symbols and dependency names to source files and line ranges, excluding generated/vendor/cache files.
4. **Planner:** combine current version, target version, evidence coverage, source matches, compatibility blockers, tests, and rollback steps into a deterministic packet.
5. **Renderers:** JSON for automation and Markdown for maintainers; include explicit unknown/partial states.
6. **CLI packaging:** installable `uip` command with `scan`, `analyze`, and `redact` subcommands.
7. **Quality:** fixtures covering Python, Node, Go, Docker, missing evidence, false positives, monorepos, redaction, invalid input, and deterministic output.
8. **SEO/discovery:** repository metadata, README search-intent sections, natural keyword coverage, GitHub topics, examples, and pinned release instructions.

## Acceptance criteria

- Standard-library runtime; no network or third-party dependency required for offline analysis.
- `uip scan` reports manifests and dependencies deterministically.
- `uip analyze` accepts JSON evidence or Markdown release notes and returns valid JSON plus Markdown.
- Findings contain evidence status, confidence, file path, line range, and recommended migration step.
- Missing official evidence is visible as `missing`, never silently treated as safe.
- Vendor, lock, binary, cache, and generated files are skipped by default.
- Secrets and private tokens are redacted before report output.
- Test suite passes in a clean Python environment.
- Skill validator passes and GitHub Actions runs tests plus metadata checks.
- Public README explains real commands, limits, safety, and search-intent use cases without keyword stuffing.
