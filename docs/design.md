# Physical Design

## Components

`src/upgrade_impact_planner/discovery.py` is the manifest boundary. It turns common repository files into normalized `Dependency` records and a small repository fingerprint. It intentionally skips vendor, cache, build, and generated locations.

`evidence.py` is the authority boundary. It accepts either a structured JSON contract or a human-supplied Markdown release note. It never fetches a URL and never treats missing text as proof of safety. Every parsed change retains its source string.

`scanner.py` is a conservative lexical impact mapper. It searches actual repository source for evidence symbols and returns relative path, line, symbol, and excerpt. It does not execute code or claim semantic correctness.

`analyzer.py` is the policy layer. It joins detected dependency state, evidence coverage, source matches, confidence, blockers, migration phases, and rollback guidance. The output remains useful when evidence or a dependency is missing because the missing state is explicit.

`render.py` provides stable JSON and human-readable Markdown. `cli.py` exposes `scan`, `analyze`, and `redact`, keeping side effects limited to writing requested report files.

## Data flow

```text
repository -> discovery -> dependency records
release evidence -> parser -> change records
change symbols + repository -> scanner -> source matches
all records -> analyzer -> impact packet -> JSON / Markdown
```

## Safety model

The MVP has no write-to-repository operation, no package installation, no arbitrary shell execution, no remote fetch, and no implicit mutation. This keeps analysis reproducible and makes it suitable for a CI report job. A future apply phase must be a separate command with explicit target, branch, approval, and post-change validation.
