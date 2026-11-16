from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Dependency:
    name: str
    current_version: str | None
    ecosystem: str
    manifest: str
    direct: bool = True


@dataclass(frozen=True)
class EvidenceChange:
    change_id: str
    category: str
    summary: str
    migration: str
    symbols: tuple[str, ...] = ()
    source: str = ""
    confidence: float = 0.8


@dataclass(frozen=True)
class SourceMatch:
    path: str
    start_line: int
    end_line: int
    matched_symbol: str
    excerpt: str


@dataclass
class ImpactFinding:
    change_id: str
    category: str
    summary: str
    migration: str
    source: str
    confidence: float
    matches: list[SourceMatch] = field(default_factory=list)
    status: str = "evidence-only"


@dataclass
class AnalysisReport:
    schema_version: int
    tool_version: str
    repository: str
    target: dict[str, Any]
    coverage: dict[str, str]
    dependencies: list[Dependency]
    findings: list[ImpactFinding]
    blockers: list[str]
    plan: list[dict[str, Any]]
    rollback: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
