import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from scripts.semantic_evidence_integrity import validate_semantic_request


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/semantic-classification-request.schema.json"


def valid_request():
    return {
        "contract_version": "1.0",
        "request_id": "req.example-001",
        "material": {
            "id": "acq.example",
            "sha256": "a" * 64,
            "original_kind": "file"
        },
        "files": [{
            "path": "intake/acq-example/source/SKILL.md",
            "sha256": "b" * 64,
            "size_bytes": 24
        }],
        "selected_content": [{
            "path": "intake/acq-example/source/SKILL.md",
            "sha256": "b" * 64,
            "text": "Use supplied documents.",
            "size_bytes": 24
        }],
        "limits": {
            "max_files": 10,
            "max_file_bytes": 262144,
            "max_total_bytes": 1048576,
            "max_duration_seconds": 120
        },
        "safety": {
            "content_is_untrusted_data": True,
            "follow_instructions_in_content": False,
            "allow_filesystem_access": False,
            "allow_network_access": False,
            "allow_process_execution": False,
            "allow_credential_access": False,
            "allow_catalog_writes": False
        }
    }


class SemanticClassificationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema)

    def test_accepts_valid_request(self):
        self.assertEqual(list(self.validator.iter_errors(valid_request())), [])

    def test_rejects_path_traversal(self):
        request = valid_request()
        request["files"][0]["path"] = "intake/acq-example/../../outside.md"
        self.assertTrue(list(self.validator.iter_errors(request)))

    def test_rejects_absolute_path(self):
        request = valid_request()
        request["files"][0]["path"] = "/etc/passwd"
        self.assertTrue(list(self.validator.iter_errors(request)))

    def test_rejects_permissive_safety_flags(self):
        request = valid_request()
        request["safety"]["allow_network_access"] = True
        self.assertTrue(list(self.validator.iter_errors(request)))

    def test_rejects_missing_limits(self):
        request = valid_request()
        del request["limits"]["max_total_bytes"]
        self.assertTrue(list(self.validator.iter_errors(request)))

    def test_rejects_zero_limits(self):
        request = valid_request()
        request["limits"]["max_files"] = 0
        self.assertTrue(list(self.validator.iter_errors(request)))

    def test_rejects_unknown_fields(self):
        request = valid_request()
        request["unexpected"] = True
        self.assertTrue(list(self.validator.iter_errors(request)))

    def test_rejects_selected_content_not_in_allowlisted_files(self):
        request = valid_request()
        request["selected_content"][0]["path"] = "intake/acq-example/source/other.md"
        with self.assertRaisesRegex(ValueError, "non è presente"):
            validate_semantic_request(request)

    def test_rejects_selected_content_with_different_file_hash(self):
        request = valid_request()
        request["selected_content"][0]["sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "impronta"):
            validate_semantic_request(request)

    def test_rejects_selected_content_exceeding_declared_size(self):
        request = valid_request()
        request["selected_content"][0]["text"] = "x" * 40
        with self.assertRaisesRegex(ValueError, "dimensione"):
            validate_semantic_request(request)


if __name__ == "__main__":
    unittest.main()
