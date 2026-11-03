import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from jsonschema import Draft202012Validator
from scripts import material_integrity
from scripts.material_integrity import (
    MaterialIntegrityError,
    load_material_record,
    verify_material,
)


class MaterialIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "catalog").mkdir()
        (self.root / "intake/acq-example/source").mkdir(parents=True)
        self.original = self.root / "intake/acq-example/source/material.md"
        self.original.write_text("# Example\n", encoding="utf-8")
        self.digest = hashlib.sha256(self.original.read_bytes()).hexdigest()
        self.record = {
            "id": "acq.example",
            "acquisition": {
                "status": "preserved",
                "original": {
                    "kind": "file",
                    "path": "intake/acq-example/source/material.md",
                    "sha256": self.digest,
                    "digest_algorithm": "sha256-file-v1",
                },
            },
        }
        self.write_catalog([self.record])

    def tearDown(self):
        self.temp.cleanup()

    def write_catalog(self, materials):
        (self.root / "catalog/materials.json").write_text(
            json.dumps({"catalog_version": "1.0", "materials": materials}),
            encoding="utf-8",
        )

    def test_result_schema_accepts_local_and_remote_results(self):
        schema_path = Path(__file__).resolve().parents[1] / "schemas/material-integrity-result.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        self.assertEqual(list(validator.iter_errors(verify_material(self.root, "acq.example"))), [])

        remote = {
            "id": "acq.remote",
            "acquisition": {"status": "received", "original": {
                "kind": "remote_reference", "uri": "https://example.org/repository"
            }},
        }
        self.write_catalog([remote])
        self.assertEqual(list(validator.iter_errors(verify_material(self.root, "acq.remote"))), [])

    def test_load_returns_record_and_catalog_references(self):
        record, catalog, catalog_path = load_material_record(self.root, "acq.example")
        self.assertEqual(record["id"], "acq.example")
        self.assertEqual(catalog["catalog_version"], "1.0")
        self.assertEqual(catalog_path.resolve(), (self.root / "catalog/materials.json").resolve())

    def test_load_rejects_missing_material(self):
        with self.assertRaises(MaterialIntegrityError) as caught:
            load_material_record(self.root, "acq.missing")
        self.assertEqual(caught.exception.code, "MATERIAL_NOT_FOUND")

    def test_load_rejects_duplicate_ids(self):
        self.write_catalog([self.record, self.record])
        with self.assertRaises(MaterialIntegrityError) as caught:
            load_material_record(self.root, "acq.example")
        self.assertEqual(caught.exception.code, "DUPLICATE_MATERIAL_ID")

    def test_verify_accepts_unchanged_file(self):
        result = verify_material(self.root, "acq.example")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["actual_digest"], self.digest)
        self.assertEqual(result["problems"], [])

    def test_verify_detects_changed_file(self):
        self.original.write_text("changed\n", encoding="utf-8")
        result = verify_material(self.root, "acq.example")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("DIGEST_MISMATCH", [item["code"] for item in result["problems"]])

    def test_verify_enforces_allowed_acquisition_states(self):
        self.record["acquisition"]["status"] = "incomplete"
        self.write_catalog([self.record])
        result = verify_material(self.root, "acq.example")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("INVALID_ACQUISITION_STATE", [item["code"] for item in result["problems"]])

    def test_verify_rejects_path_traversal(self):
        self.record["acquisition"]["original"]["path"] = "intake/../../outside.txt"
        self.write_catalog([self.record])
        result = verify_material(self.root, "acq.example")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("INVALID_ORIGINAL_PATH", [item["code"] for item in result["problems"]])

    def test_verify_rejects_symlink_in_original_path(self):
        link = self.root / "intake/acq-example/source/link.md"
        try:
            link.symlink_to(self.original)
        except (OSError, NotImplementedError):
            self.skipTest("Collegamenti simbolici non disponibili in questo ambiente")
        self.record["acquisition"]["original"]["path"] = "intake/acq-example/source/link.md"
        self.record["acquisition"]["original"]["sha256"] = self.digest
        self.write_catalog([self.record])
        result = verify_material(self.root, "acq.example")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("SYMLINK_NOT_ALLOWED", [item["code"] for item in result["problems"]])

    def test_verify_checks_expected_digest(self):
        result = verify_material(self.root, "acq.example", expected_digest="0" * 64)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("EXPECTED_DIGEST_MISMATCH", [item["code"] for item in result["problems"]])

    def test_verify_rejects_unknown_digest_algorithm(self):
        self.record["acquisition"]["original"]["digest_algorithm"] = "sha512"
        self.write_catalog([self.record])
        result = verify_material(self.root, "acq.example")
        self.assertEqual(result["status"], "failed")
        self.assertIn("UNSUPPORTED_DIGEST_ALGORITHM", [item["code"] for item in result["problems"]])

    def test_remote_reference_is_not_reported_as_verified(self):
        remote = {
            "id": "acq.remote",
            "acquisition": {
                "status": "received",
                "original": {
                    "kind": "remote_reference",
                    "uri": "https://example.org/repository",
                },
            },
        }
        self.write_catalog([remote])
        result = verify_material(self.root, "acq.remote")
        self.assertEqual(result["status"], "not_applicable")
        self.assertIsNone(result["actual_digest"])
        self.assertIn("REMOTE_CONTENT_NOT_CHECKED", [item["code"] for item in result["problems"]])

    def test_verify_preserves_legacy_directory_fingerprint(self):
        folder = self.root / "intake/acq-example/source"
        (folder / "empty").mkdir()
        digest = hashlib.sha256()
        file_path = folder / "material.md"
        digest.update(b"material.md\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")
        legacy_record = {
            "id": "acq.legacy",
            "acquisition": {
                "status": "preserved",
                "original": {
                    "kind": "directory",
                    "path": "intake/acq-example/source",
                    "sha256": digest.hexdigest(),
                },
            },
        }
        self.write_catalog([legacy_record])
        result = verify_material(self.root, "acq.legacy")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["digest_algorithm"], "sha256-tree-legacy")

    def test_file_hash_rejects_path_replaced_with_symlink_before_open(self):
        outside = self.root / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        original_open = material_integrity._open_fd

        def replace_then_open(path, flags, *args, **kwargs):
            if Path(path) == self.original:
                self.original.unlink()
                self.original.symlink_to(outside)
            return original_open(path, flags, *args, **kwargs)

        try:
            with patch("scripts.material_integrity._open_fd", side_effect=replace_then_open):
                with self.assertRaises((OSError, MaterialIntegrityError)):
                    material_integrity._sha256_file(self.original)
        except (OSError, NotImplementedError):
            self.skipTest("Collegamenti simbolici non disponibili in questo ambiente")

    def test_catalog_symlink_is_rejected(self):
        catalog = self.root / "catalog/materials.json"
        backup = self.root / "catalog/materials.backup"
        catalog.rename(backup)
        try:
            catalog.symlink_to(backup)
        except (OSError, NotImplementedError):
            backup.rename(catalog)
            self.skipTest("Collegamenti simbolici non disponibili in questo ambiente")
        result = verify_material(self.root, "acq.example")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("SYMLINK_NOT_ALLOWED", [item["code"] for item in result["problems"]])


if __name__ == "__main__":
    unittest.main()
