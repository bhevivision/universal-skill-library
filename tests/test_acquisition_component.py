import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.acquire_material import acquire_material, acquire_remote_material
from scripts.validate_library import validate_repository
from test_validate_library import make_repo


class AcquisitionComponentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "library"
        self.root.mkdir()
        make_repo(self.root)
        self.incoming = Path(self.temp.name) / "incoming"
        self.incoming.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def materials(self):
        return json.loads((self.root / "catalog/materials.json").read_text(encoding="utf-8"))["materials"]

    def test_acquires_file_without_changing_source_and_records_hash(self):
        source = self.incoming / "procedure.txt"
        original = b"Procedura originale\n"
        source.write_bytes(original)

        record = acquire_material(self.root, source, "acq.procedure")

        stored = self.root / record["acquisition"]["original"]["path"]
        self.assertEqual(stored.read_bytes(), original)
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(record["acquisition"]["original"]["kind"], "file")
        self.assertEqual(len(record["acquisition"]["original"]["sha256"]), 64)
        self.assertEqual(record["classification"]["status"], "not_examined")
        self.assertEqual(record["verification"]["status"], "not_verified")
        self.assertEqual(len(self.materials()), 1)
        self.assertEqual(validate_repository(self.root), [])

    def test_acquires_directory_with_all_nested_files(self):
        source = self.incoming / "package"
        (source / "references").mkdir(parents=True)
        (source / "instructions.md").write_text("Istruzioni\n", encoding="utf-8")
        (source / "references" / "guide.txt").write_text("Guida\n", encoding="utf-8")

        record = acquire_material(self.root, source, "acq.package", kind="package")

        stored = self.root / record["acquisition"]["original"]["path"]
        self.assertTrue((stored / "references" / "guide.txt").is_file())
        self.assertEqual((stored / "instructions.md").read_text(encoding="utf-8"), "Istruzioni\n")
        self.assertEqual(record["acquisition"]["original"]["kind"], "package")
        self.assertEqual(validate_repository(self.root), [])

    def test_keeps_archive_as_opaque_original_file(self):
        source = self.incoming / "bundle.zip"
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("payload.txt", "non estrarre")
        original = source.read_bytes()

        record = acquire_material(self.root, source, "acq.archive")

        stored = self.root / record["acquisition"]["original"]["path"]
        self.assertEqual(stored.read_bytes(), original)
        self.assertTrue(stored.is_file())
        self.assertEqual(record["acquisition"]["original"]["kind"], "archive")

    def test_rejects_duplicate_identifier_without_overwriting_existing_material(self):
        source = self.incoming / "one.txt"
        source.write_text("uno", encoding="utf-8")
        first = acquire_material(self.root, source, "acq.same")
        second_source = self.incoming / "two.txt"
        second_source.write_text("due", encoding="utf-8")

        with self.assertRaises(ValueError):
            acquire_material(self.root, second_source, "acq.same")

        stored = self.root / first["acquisition"]["original"]["path"]
        self.assertEqual(stored.read_text(encoding="utf-8"), "uno")
        self.assertEqual(len(self.materials()), 1)

    def test_rejects_symlink_in_source_tree(self):
        source = self.incoming / "folder"
        source.mkdir()
        target = self.incoming / "secret.txt"
        target.write_text("segreto", encoding="utf-8")
        try:
            (source / "link.txt").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Il sistema operativo non consente la creazione di collegamenti simbolici.")

        with self.assertRaises(ValueError):
            acquire_material(self.root, source, "acq.symlink")

        self.assertEqual(self.materials(), [])

    def test_failed_copy_leaves_no_catalog_record_or_partial_destination(self):
        source = self.incoming / "failure.txt"
        source.write_text("contenuto", encoding="utf-8")

        with patch("scripts.acquire_material._copy_file_bounded", side_effect=OSError("copia interrotta")):
            with self.assertRaises(OSError):
                acquire_material(self.root, source, "acq.failure")

        self.assertEqual(self.materials(), [])
        self.assertFalse((self.root / "intake/acq-failure").exists())

    def test_rejects_existing_destination_even_if_catalog_has_no_record(self):
        source = self.incoming / "collision.txt"
        source.write_text("contenuto", encoding="utf-8")
        destination = self.root / "intake/acq-collision"
        destination.mkdir(parents=True)
        (destination / "keep.txt").write_text("non sovrascrivere", encoding="utf-8")

        with self.assertRaises(ValueError):
            acquire_material(self.root, source, "acq.collision")

        self.assertEqual((destination / "keep.txt").read_text(encoding="utf-8"), "non sovrascrivere")

    def test_streaming_copy_enforces_limits_if_source_grows_after_preinspection(self):
        from scripts import acquire_material as acquisition
        source = self.incoming / "growing"
        source.mkdir()
        target = source / "material.txt"
        target.write_bytes(b"small")
        original_inspect = acquisition._inspect_source

        def inspect_then_grow(path):
            result = original_inspect(path)
            target.write_bytes(b"x" * 64)
            return result

        with patch("scripts.acquire_material.MAX_ACQUISITION_BYTES", 16), patch(
            "scripts.acquire_material._inspect_source", side_effect=inspect_then_grow
        ):
            with self.assertRaisesRegex(ValueError, "limite massimo"):
                acquire_material(self.root, source, "acq.growing")

        self.assertEqual(self.materials(), [])
        self.assertFalse((self.root / "intake/acq-growing").exists())

    def test_directory_inventory_stops_at_configured_file_limit(self):
        from scripts import acquire_material as acquisition
        source = self.incoming / "many"
        source.mkdir()
        for name in ("a.txt", "b.txt", "c.txt"):
            (source / name).write_text(name, encoding="utf-8")
        with patch("scripts.acquire_material.MAX_ACQUISITION_FILES", 2):
            with self.assertRaisesRegex(ValueError, "numero massimo"):
                acquisition._inspect_source(source)

    def test_registers_remote_reference_without_claiming_local_copy(self):
        record = acquire_remote_material(
            self.root, "acq.remote", "https://example.org/material.zip",
            name="Materiale remoto"
        )

        self.assertEqual(record["acquisition"]["original"]["kind"], "remote_reference")
        self.assertEqual(record["acquisition"]["original"]["uri"], "https://example.org/material.zip")
        self.assertNotIn("path", record["acquisition"]["original"])
        self.assertEqual(record["acquisition"]["status"], "received")
        self.assertEqual(validate_repository(self.root), [])

    def test_rejects_invalid_identifier_and_nonexistent_source(self):
        source = self.incoming / "valid.txt"
        source.write_text("x", encoding="utf-8")
        with self.assertRaises(ValueError):
            acquire_material(self.root, source, "../escape")
        with self.assertRaises(FileNotFoundError):
            acquire_material(self.root, self.incoming / "missing.txt", "acq.missing")

    def test_does_not_overwrite_existing_catalog_content(self):
        source = self.incoming / "new.txt"
        source.write_text("nuovo", encoding="utf-8")
        catalog = self.root / "catalog/materials.json"
        before = catalog.read_bytes()

        acquire_material(self.root, source, "acq.new")

        after = json.loads(catalog.read_text(encoding="utf-8"))
        self.assertEqual(after["catalog_version"], "1.0")
        self.assertEqual(len(after["materials"]), 1)
        self.assertNotEqual(catalog.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
