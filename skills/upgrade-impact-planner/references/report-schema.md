# Report schema

The JSON renderer emits `schema_version`, `tool_version`, `repository`, `target`, `coverage`, `dependencies`, `findings`, `blockers`, `plan`, `rollback`, and `warnings`.

Each finding includes `change_id`, `category`, `summary`, `migration`, `source`, `confidence`, `status`, and zero or more `matches`. A match contains a repository-relative `path`, `start_line`, `end_line`, `matched_symbol`, and short `excerpt`.

`coverage.official_evidence` is `complete`, `partial`, `missing`, or `blocked`. Missing or partial evidence must be treated as a review blocker. `status=confirmed` means a lexical source match was found; it is not a runtime compatibility guarantee.
