import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SRC = ROOT / "src"
FIX = ROOT / "tests" / "fixtures"

sys.path.insert(0, str(SRC))
from upgrade_impact_planner.analyzer import analyze
from upgrade_impact_planner.discovery import discover_dependencies
from upgrade_impact_planner.evidence import from_markdown
from upgrade_impact_planner.render import render_markdown
from upgrade_impact_planner.cli import redact


class CoreTests(unittest.TestCase):
    def test_discovery_finds_node_direct_dependencies(self):
        deps = discover_dependencies(FIX / "sample_repo")
        names = {d.name for d in deps}
        self.assertIn("demo-lib", names)
        self.assertIn("unrelated-lib", names)
        self.assertEqual(next(d for d in deps if d.name == "demo-lib").current_version, "^1.4.0")

    def test_discovery_supports_python_go_rust_and_docker(self):
        deps = discover_dependencies(FIX / "multi_repo")
        ecosystems = {d.ecosystem for d in deps}
        self.assertTrue({"python", "go", "rust", "docker"}.issubset(ecosystems))
        self.assertIn("requests", {d.name for d in deps})
        self.assertIn("github.com/stretchr/testify", {d.name for d in deps})
        self.assertIn("serde", {d.name for d in deps})
        self.assertIn("python", {d.name for d in deps})

    def test_json_evidence_maps_confirmed_source_match(self):
        report = analyze(FIX / "sample_repo", "demo-lib", "2.0.0", FIX / "demo-lib-upgrade.json")
        self.assertEqual(report.coverage["official_evidence"], "complete")
        self.assertEqual(report.target["from"], "^1.4.0")
        removed = next(f for f in report.findings if f.change_id == "demo-old-api-removed")
        self.assertEqual(removed.status, "confirmed")
        self.assertEqual(removed.matches[0].path, "src/app.js")
        self.assertEqual(removed.matches[0].start_line, 1)
        self.assertIn("oldApi", removed.matches[0].excerpt)

    def test_scanner_ignores_vendor_paths(self):
        report = analyze(FIX / "multi_repo", "requests", "3.0.0", FIX / "demo-lib-upgrade.json")
        self.assertFalse(any(m.path.startswith("vendor/") for finding in report.findings for m in finding.matches))

    def test_missing_evidence_is_explicit_blocker(self):
        report = analyze(FIX / "sample_repo", "demo-lib", "2.0.0")
        self.assertEqual(report.coverage["official_evidence"], "missing")
        self.assertTrue(any("evidence" in item.lower() for item in report.blockers))
        self.assertIn("No official release notes", " ".join(report.warnings))

    def test_markdown_evidence_parses_and_renders(self):
        changes, status = from_markdown(FIX / "demo-lib-upgrade.md")
        self.assertEqual(status, "complete")
        self.assertGreaterEqual(len(changes), 2)
        report = analyze(FIX / "sample_repo", "demo-lib", "2.0.0", FIX / "demo-lib-upgrade.md")
        markdown = render_markdown(report)
        self.assertIn("Upgrade Impact Report", markdown)
        self.assertIn("report-only", markdown)

    def test_redaction(self):
        value = "Authorization gh" + "p_abcdefghijklmnopqrstuvwxyz123456"
        output = redact(value)
        self.assertNotIn("ghp_", output)
        self.assertIn("[REDACTED_SECRET]", output)

    def test_cli_scan_and_analyze(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            scan = subprocess.run([sys.executable, "-m", "upgrade_impact_planner", "scan", str(FIX / "sample_repo")], cwd=ROOT, env={"PYTHONPATH": str(SRC)}, text=True, capture_output=True)
            self.assertEqual(scan.returncode, 0, scan.stderr)
            self.assertIn("demo-lib", scan.stdout)
            json_out = out / "impact.json"
            md_out = out / "impact.md"
            result = subprocess.run([sys.executable, "-m", "upgrade_impact_planner", "analyze", str(FIX / "sample_repo"), "--target", "demo-lib", "--to", "2.0.0", "--evidence", str(FIX / "demo-lib-upgrade.json"), "--json", str(json_out), "--markdown", str(md_out)], cwd=ROOT, env={"PYTHONPATH": str(SRC)}, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(json_out.read_text())
            self.assertEqual(data["target"]["to"], "2.0.0")
            self.assertTrue(md_out.exists())


if __name__ == "__main__":
    unittest.main()
