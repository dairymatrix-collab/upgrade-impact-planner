#!/usr/bin/env python3
"""Bundled Upgrade Impact Planner runtime for skill-only installations."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from uip_runtime.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
