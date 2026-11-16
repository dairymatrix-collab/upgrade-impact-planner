# Contributing

Use the standard library where practical so offline analysis remains easy to install. Add a fixture before changing parser behavior. Run `python -m unittest discover -s tests -v`, `python -m compileall -q src tests`, and the skill validator before opening a pull request.

Every finding must preserve its source evidence, confidence, and repository location. Do not add behavior that edits, installs, commits, or deploys by default.
