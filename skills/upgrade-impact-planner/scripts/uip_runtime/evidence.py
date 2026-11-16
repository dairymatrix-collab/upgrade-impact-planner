from __future__ import annotations
import json
import re
from pathlib import Path
from .models import EvidenceChange

CATEGORIES = {"breaking", "removed", "renamed", "deprecated", "config", "runtime", "dependency", "behavior", "security", "other"}

def _category(text: str) -> str:
    low=text.lower()
    for key, words in (("breaking", ("breaking", "incompatible")), ("removed", ("removed", "no longer supported")), ("renamed", ("renamed", "rename")), ("deprecated", ("deprecat",)), ("config", ("config", "option", "setting")), ("runtime", ("node", "python", "java", "runtime", "engine")), ("dependency", ("peer", "dependency")), ("security", ("security", "permission", "auth")), ("behavior", ("default", "behavior", "behaviour"))):
        if any(word in low for word in words): return key
    return "other"


def _symbols(text: str) -> tuple[str, ...]:
    found=re.findall(r"`([^`]+)`|\b[A-Za-z_][A-Za-z0-9_.:-]{2,}\b", text)
    stop={"the","and","with","from","this","that","must","will","your","change","version","upgrade","breaking"}
    return tuple(dict.fromkeys(x for x in found if x.lower() not in stop and not x.isdigit()))[:12]


def from_json(path: Path) -> tuple[list[EvidenceChange], str]:
    data=json.loads(path.read_text(encoding="utf-8"))
    raw=data.get("changes", data if isinstance(data, list) else [])
    result=[]
    for index, item in enumerate(raw, 1):
        if not isinstance(item, dict): continue
        summary=str(item.get("summary", "")).strip()
        if not summary: continue
        result.append(EvidenceChange(str(item.get("id", f"change-{index}")), str(item.get("category", _category(summary))), summary, str(item.get("migration", "Review official migration guidance")), tuple(item.get("symbols", _symbols(summary))), str(item.get("source", path)), float(item.get("confidence", 0.9))))
    return result, "complete" if result else "missing"


def from_markdown(path: Path) -> tuple[list[EvidenceChange], str]:
    text=path.read_text(encoding="utf-8")
    lines=text.splitlines(); result=[]; current=None; migration=[]
    def flush():
        nonlocal current, migration
        if current:
            summary=current["summary"].strip()
            result.append(EvidenceChange(current["id"], _category(summary), summary, " ".join(migration).strip() or "Review official migration guidance", _symbols(summary), str(path), 0.75))
        current=None; migration=[]
    for line in lines:
        heading=re.match(r"^#{1,4}\s+(.+)$", line)
        if heading:
            title=heading.group(1).strip()
            if current: flush()
            if any(word in title.lower() for word in ("breaking", "removed", "deprecated", "migration", "change", "upgrade")):
                current={"id": f"change-{len(result)+1}", "summary": title}
            continue
        if current:
            clean=line.strip(" -*\t")
            if clean: migration.append(clean)
    flush()
    return result, "complete" if result else "partial"


def load_evidence(path: Path | None) -> tuple[list[EvidenceChange], str, list[str]]:
    if path is None: return [], "missing", ["No official release notes or migration guide was supplied."]
    try:
        if path.suffix.lower() == ".json": changes, status=from_json(path)
        else: changes, status=from_markdown(path)
        return changes, status, [] if changes else [f"Evidence file {path} contained no recognizable changes."]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], "blocked", [f"Could not read evidence file: {exc}"]
