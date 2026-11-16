# Upgrade Impact Planner

**Evidence-first dependency upgrade, breaking-change analysis, deprecated API migration planning, and framework upgrade impact analysis for real repositories.**

A version bump tells you what changed in a dependency graph. **Upgrade Impact Planner tells you what may break in your code, where it appears, what official evidence supports the claim, and how to migrate safely.** It is a runnable Python CLI plus an Agent Skill for GitHub Copilot, Claude Code, Codex, Cursor, Gemini CLI, and other compatible agents.

## Why this exists

Dependabot and dependency review are excellent at surfacing available updates, changed manifests, and known vulnerabilities. They do not always produce a repository-specific breaking-change map: deprecated symbols, removed APIs, changed defaults, runtime requirements, peer conflicts, test gaps, and rollback steps. This project fills that planning gap without pretending that a static scan proves runtime compatibility.

## What it does

- Detects dependencies in `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, and Dockerfiles.
- Reads structured JSON evidence or official Markdown release notes and migration guides.
- Classifies changes such as breaking behavior, removed or renamed APIs, deprecations, configuration changes, runtime requirements, peer dependencies, security changes, and changed defaults.
- Maps evidence symbols to real repository files and line numbers.
- Produces deterministic JSON for automation and Markdown for maintainers.
- Shows missing or partial evidence as a blocker instead of calling an upgrade safe.
- Generates preparation, code-migration, validation, cleanup, and rollback steps.
- Redacts common GitHub and provider token shapes before sharing output.
- Runs offline with the Python standard library; no network call is required for analysis.

## Install

```bash
python -m pip install .
# or for development
python -m pip install -e .
```

## Quick example

```bash
uip scan ./my-repository --json .uip/dependencies.json
uip analyze ./my-repository \
  --target requests \
  --to 3.0.0 \
  --evidence ./evidence/requests-3-migration.md \
  --json .uip/requests-3-impact.json \
  --markdown .uip/requests-3-impact.md
```

The command is read-only. It does not install `requests`, edit code, create a branch, commit, push, or deploy.

### Run without installing Python package

The skill also contains the physical runtime under `skills/upgrade-impact-planner/scripts/`. This is useful when an agent installs only the skill directory:

```bash
python skills/upgrade-impact-planner/scripts/uip.py scan ./my-repository
python skills/upgrade-impact-planner/scripts/uip.py analyze ./my-repository --target requests --to 3.0.0 --evidence ./migration.md
```

## Structured evidence

For reliable automation, provide a JSON file:

```json
{
  "changes": [
    {
      "id": "requests-removed-old-api",
      "category": "removed",
      "summary": "The legacy request helper was removed",
      "migration": "Use the session-based helper described in the official guide",
      "symbols": ["legacy_request", "requests.Session"],
      "source": "https://vendor.example/migration",
      "confidence": 0.95
    }
  ]
}
```

The report will cite the source and show every matching file/line. If the source file is missing or contains no recognizable changes, the report remains explicitly incomplete.

## Search-intent coverage

This project is intentionally discoverable for real developer searches including **dependency upgrade breaking changes**, **breaking change migration plan**, **deprecated API migration**, **upgrade impact analysis**, **Dependabot major update review**, **framework upgrade checklist**, **package upgrade code changes**, **compatibility audit**, and **migration guide analyzer**. These phrases describe actual capabilities; they are not unrelated keyword stuffing.

## Agent Skill

The skill instructions live at [`skills/upgrade-impact-planner/SKILL.md`](skills/upgrade-impact-planner/SKILL.md). Install a tagged release with the compatible skills CLI:

```bash
npx skills add dairymatrix-collab/upgrade-impact-planner
```

If your agent does not support the skills CLI, point it at the `skills/upgrade-impact-planner` directory and install the Python package separately when you need the executable.

## Safety and limitations

This is an impact planner, not a compiler, test runner, package manager, or guarantee of compatibility. It does not execute arbitrary code or fetch remote documentation automatically. Official evidence must be supplied by the user or a surrounding workflow. A confirmed text match can still be a false positive; review the context and run the repository's own tests before merging. Unsupported manifests, generated code, dynamic imports, reflection, and runtime-only behavior may be missed.

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
python /home/ubuntu/skills/skill-creator/scripts/quick_validate.py --path skills/upgrade-impact-planner
```

See [`PLAN.md`](PLAN.md) for acceptance criteria and [`docs/design.md`](docs/design.md) for the physical architecture.

## License

MIT. See [`LICENSE`](LICENSE).
