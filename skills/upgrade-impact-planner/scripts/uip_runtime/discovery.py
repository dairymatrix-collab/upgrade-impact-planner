from __future__ import annotations
import json
import re
import tomllib
from pathlib import Path
from .models import Dependency

IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "vendor", "dist", "build", "target", ".uip"}


def _version(value: object) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    return None


def discover_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and not any(part in IGNORE_DIRS for part in p.parts)]


def _node(path: Path) -> list[Dependency]:
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError): return []
    result = []
    for section, direct in (("dependencies", True), ("devDependencies", True), ("peerDependencies", True), ("optionalDependencies", True)):
        for name, value in (data.get(section) or {}).items(): result.append(Dependency(name, _version(value), "npm", str(path), direct))
    return result


def _python(path: Path) -> list[Dependency]:
    result = []
    try:
        text = path.read_text(encoding="utf-8")
        if path.name == "pyproject.toml":
            data = tomllib.loads(text)
            raw = data.get("project", {}).get("dependencies", [])
            for item in raw:
                match = re.match(r"([A-Za-z0-9_.-]+)\s*(.*)", item)
                if match: result.append(Dependency(match.group(1), match.group(2).strip() or None, "python", str(path)))
        else:
            for line in text.splitlines():
                line = line.split("#", 1)[0].strip()
                match = re.match(r"([A-Za-z0-9_.-]+)\s*([<>=!~].*)?$", line)
                if match and match.group(1).lower() not in {"-e", "git"}: result.append(Dependency(match.group(1), (match.group(2) or "").strip() or None, "python", str(path)))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError): pass
    return result


def _go(path: Path) -> list[Dependency]:
    result=[]
    try: text=path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError): return result
    for line in text.splitlines():
        match=re.match(r"\s*(?:require\s+)?([\w./-]+)\s+(v[^\s]+)", line)
        if match: result.append(Dependency(match.group(1), match.group(2), "go", str(path)))
    return result


def _cargo(path: Path) -> list[Dependency]:
    result=[]
    try: data=tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError): return result
    for section in ("dependencies", "dev-dependencies", "build-dependencies"):
        for name, value in (data.get(section) or {}).items():
            version=value if isinstance(value, str) else (value or {}).get("version")
            result.append(Dependency(name, _version(version), "rust", str(path)))
    return result


def _docker(path: Path) -> list[Dependency]:
    result=[]
    try: lines=path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError): return result
    for line in lines:
        match=re.match(r"\s*FROM\s+([^\s]+)", line, re.I)
        if match:
            image=match.group(1); name, _, version=image.partition(":")
            result.append(Dependency(name, version or "latest", "docker", str(path)))
    return result


def discover_dependencies(root: Path) -> list[Dependency]:
    result=[]
    for path in discover_files(root):
        if path.name == "package.json": result += _node(path)
        elif path.name in {"requirements.txt", "requirements-dev.txt", "requirements-test.txt"}: result += _python(path)
        elif path.name == "pyproject.toml": result += _python(path)
        elif path.name == "go.mod": result += _go(path)
        elif path.name == "Cargo.toml": result += _cargo(path)
        elif path.name == "Dockerfile" or path.name.startswith("Dockerfile."): result += _docker(path)
    return result


def repository_fingerprint(root: Path) -> dict[str, object]:
    files=discover_files(root)
    names={p.name for p in files}
    languages=[]
    for name, language in (("package.json","javascript"),("pyproject.toml","python"),("requirements.txt","python"),("go.mod","go"),("Cargo.toml","rust"),("Dockerfile","docker")):
        if name in names and language not in languages: languages.append(language)
    return {"languages": languages, "file_count": len(files), "manifests": sorted(name for name in names if name in {"package.json","pyproject.toml","requirements.txt","go.mod","Cargo.toml","Dockerfile"})}
