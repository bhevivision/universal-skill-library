import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.semantic_adapter_diagnostics import write_diagnostic


class SemanticAdapterDiagnosticsTests(unittest.TestCase):
    def test_does_not_write_when_diagnostics_are_disabled(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {}, clear=True):
                write_diagnostic("raw_response", "eval:sample-01", {"raw": "model output"})
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_writes_each_stage_as_json_when_explicitly_enabled(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {"SEMANTIC_ADAPTER_DIAGNOSTICS_DIR": temp}, clear=True):
                path = write_diagnostic("normalized_output", "eval:sample-01", {"evidence_refs": ["ev.sample-001"]})
            self.assertIsNotNone(path)
            saved = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(saved["stage"], "normalized_output")
            self.assertEqual(saved["request_id"], "eval:sample-01")
            self.assertEqual(saved["payload"]["evidence_refs"], ["ev.sample-001"])

    def test_rejects_unknown_stage_and_unsafe_request_identifier(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {"SEMANTIC_ADAPTER_DIAGNOSTICS_DIR": temp}, clear=True):
                with self.assertRaises(ValueError):
                    write_diagnostic("../raw", "eval:sample-01", {})
                with self.assertRaises(ValueError):
                    write_diagnostic("raw_response", "../../outside", {})
            self.assertEqual(list(Path(temp).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
