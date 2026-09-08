import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from formal_pipeline import execute_discovery
from observation_package import validate_package


DBC_TEXT = '''VERSION ""
NS_ :
BS_:
BU_: ECU
BO_ 256 Known: 1 ECU
 SG_ value : 0|1@1+ (1,0) [0|1] "" ECU
'''


class FormalPipelineContractTest(unittest.TestCase):
    def test_default_entry_is_legacy_noop(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "src" / "formal_pipeline.py")],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        self.assertEqual("LEGACY_UNCHANGED", json.loads(completed.stdout)["status"])

    def test_explicit_discovery_freezes_package_and_stops(self):
        base = ROOT / "output"
        with tempfile.TemporaryDirectory(dir=base) as temp:
            folder = Path(temp)
            asc = folder / "tiny.asc"
            dbc = folder / "tiny.dbc"
            charter_path = folder / "charter.json"
            asc.write_text("0.000000 1 100 Rx d 1 00\n0.100000 1 222 Rx d 1 01\n", encoding="utf-8")
            dbc.write_text(DBC_TEXT, encoding="utf-8")
            asc_ref = str(asc.relative_to(ROOT))
            dbc_ref = str(dbc.relative_to(ROOT))
            charter_path.write_text(json.dumps({
                "charter_version": "analysis-charter-v1",
                "experiment_id": "SYNTHETIC",
                "purpose": "contract",
                "system_scope": "test",
                "analysis_scope": "full bus",
                "l3_prior_refs": [],
                "evidence_requirements": ["future only"],
                "allowed_data_sources": [asc_ref, dbc_ref],
                "asc_ref": asc_ref,
                "dbc_refs": [dbc_ref],
                "time_policy": {"mode": "STATIC"},
                "known_signal_hints": ["value"],
            }), encoding="utf-8")
            run_dir, audit = execute_discovery(charter_path, folder / "runs")
            package = json.loads((run_dir / "observation_package.json").read_text(encoding="utf-8"))
            stored_audit = json.loads((run_dir / "runtime_audit.json").read_text(encoding="utf-8"))

            validate_package(package)
            self.assertEqual("DISCOVERY_COMPLETE", audit["exit_status"])
            self.assertEqual(1, audit["asc_parse_count"])
            self.assertEqual(0, audit["llm_calls"])
            self.assertEqual(0, audit["semantic_reasoning_calls"])
            self.assertEqual(0, audit["evidence_mapping_calls"])
            self.assertEqual(0, audit["renderer_calls"])
            self.assertEqual(package["package_hash"], stored_audit["package_hash"])
            self.assertNotIn("reasoning", package)
            self.assertEqual(2, len(package["observations"]))
            self.assertTrue(package["closure"]["closed"])


if __name__ == "__main__":
    unittest.main()
