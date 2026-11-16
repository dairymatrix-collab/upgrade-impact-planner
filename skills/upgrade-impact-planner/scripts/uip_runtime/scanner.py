from __future__ import annotations
from pathlib import Path
from .discovery import IGNORE_DIRS, discover_files
from .models import SourceMatch

SKIP_SUFFIXES={".lock", ".map", ".min.js", ".pyc", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".gz", ".whl"}

def scan_symbols(root: Path, symbols: tuple[str, ...], max_matches: int=500) -> list[SourceMatch]:
    needles=tuple(dict.fromkeys(s for s in symbols if len(s)>=3))
    if not needles: return []
    matches=[]
    for path in discover_files(root):
        if path.suffix.lower() in SKIP_SUFFIXES or path.name.startswith("package-lock") or path.name.endswith(".generated.cs"): continue
        try: lines=path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError): continue
        for index, line in enumerate(lines, 1):
            hit=next((s for s in needles if s in line), None)
            if hit:
                matches.append(SourceMatch(str(path.relative_to(root)), index, index, hit, line.strip()[:240]))
                if len(matches)>=max_matches: return matches
    return matches
