from __future__ import annotations
import argparse
from pathlib import Path
from .analyzer import analyze
from .discovery import discover_dependencies, repository_fingerprint
from .render import render_json, render_markdown

SECRET_PATTERNS=("ghp_", "gho_", "ghu_", "github_pat_", "sk-", "AKIA")

def redact(text: str) -> str:
    for marker in SECRET_PATTERNS:
        start=0
        while True:
            index=text.find(marker, start)
            if index < 0: break
            end=index+len(marker)
            while end < len(text) and text[end] not in " \t\r\n,;)}]\\\"'": end += 1
            text=text[:index]+"[REDACTED_SECRET]"+text[end:]
            start=index+len("[REDACTED_SECRET]")
    return text


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(prog="uip", description="Evidence-first dependency upgrade, breaking-change, deprecated API, and migration impact planner")
    sub=parser.add_subparsers(dest="command", required=True)
    scan=sub.add_parser("scan", help="discover supported manifests and dependencies")
    scan.add_argument("repo", type=Path)
    scan.add_argument("--json", dest="json_output", type=Path)
    ana=sub.add_parser("analyze", help="generate a read-only upgrade impact report")
    ana.add_argument("repo", type=Path)
    ana.add_argument("--target", required=True, help="dependency, framework, runtime, or API name")
    ana.add_argument("--to", dest="to_version")
    ana.add_argument("--evidence", type=Path, help="official release notes/migration Markdown or structured JSON")
    ana.add_argument("--json", dest="json_output", type=Path)
    ana.add_argument("--markdown", dest="markdown_output", type=Path)
    red=sub.add_parser("redact", help="redact common credentials from a text file")
    red.add_argument("input", type=Path)
    red.add_argument("--output", type=Path)
    args=parser.parse_args(argv)
    root=args.repo.resolve() if hasattr(args,"repo") else None
    if args.command == "scan":
        if not root.is_dir(): parser.error("repo must be an existing directory")
        data={"repository":str(root),"fingerprint":repository_fingerprint(root),"dependencies":[d.__dict__ for d in discover_dependencies(root)]}
        text=__import__("json").dumps(data, indent=2, sort_keys=True)+"\n"
        if args.json_output: args.json_output.write_text(text, encoding="utf-8")
        else: print(text, end="")
        return 0
    if args.command == "analyze":
        if not root.is_dir(): parser.error("repo must be an existing directory")
        report=analyze(root,args.target,args.to_version,args.evidence)
        j=redact(render_json(report)); md=redact(render_markdown(report))
        if args.json_output: args.json_output.write_text(j, encoding="utf-8")
        else: print(j, end="")
        if args.markdown_output: args.markdown_output.write_text(md, encoding="utf-8")
        return 0
    text=redact(args.input.read_text(encoding="utf-8"))
    if args.output: args.output.write_text(text, encoding="utf-8")
    else: print(text, end="")
    return 0

if __name__ == "__main__": raise SystemExit(main())
