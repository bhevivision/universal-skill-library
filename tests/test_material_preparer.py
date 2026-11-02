import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.classify_material import _read_evidence
from scripts.material_preparer import prepare_material


TEXT_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".rst", ".json", ".yaml", ".yml",
    ".toml", ".py", ".js", ".ts", ".sh", ".ps1", ".bat", ".xml",
    ".html", ".css",
}


def digest_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_directory(path):
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*"), key=lambda entry: entry.relative_to(path).as_posix()):
        relative = item.relative_to(path).as_posix().encode("utf-8")
        if item.is_dir() and not item.is_symlink():
            digest.update(b"D\\0" + relative + b"\\0")
        elif item.is_file() and not item.is_symlink():
            digest.update(b"F\\0" + relative + b"\\0")
            digest.update(item.read_bytes())
            digest.update(b"\\0")
    return digest.hexdigest()


class MaterialPreparerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "catalog").mkdir()
        self.source = self.root / "intake/acq-sample/source"
        self.source.mkdir(parents=True)
        self.write_catalog_for_directory()

    def tearDown(self):
        self.temp.cleanup()

    def write_catalog_for_directory(self, *, kind="directory", state="preserved"):
        record = {
            "id": "acq.sample",
            "acquisition": {
                "status": state,
                "original": {
                    "kind": kind,
                    "path": "intake/acq-sample/source",
                    "sha256": digest_directory(self.source),
                    "digest_algorithm": "sha256-tree-v2",
                },
            },
        }
        self.write_catalog([record])

    def write_catalog(self, materials):
        (self.root / "catalog/materials.json").write_text(
            json.dumps({"catalog_version": "1.0", "materials": materials}),
            encoding="utf-8",
        )

    def prepare(self):
        return prepare_material(self.root, "acq.sample")

    def test_prepares_single_supported_text_file(self):
        original = self.source / "guide.md"
        original.write_text("# Guida\\nTesto.\\n", encoding="utf-8")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "completed")
        self.assertEqual([item["source"] for item in result["files"]], [
            "intake/acq-sample/source/guide.md"
        ])
        self.assertEqual(result["files"][0]["content"], "# Guida\\nTesto.\\n")

    def test_selects_directory_files_in_path_sorted_order(self):
        (self.source / "zeta.txt").write_text("Z", encoding="utf-8")
        (self.source / "nested").mkdir()
        (self.source / "nested" / "alpha.md").write_text("A", encoding="utf-8")
        (self.source / ".hidden.txt").write_text("H", encoding="utf-8")
        (self.source / "image.png").write_bytes(b"not text")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(
            [item["source"] for item in result["files"]],
            [
                "intake/acq-sample/source/.hidden.txt",
                "intake/acq-sample/source/nested/alpha.md",
                "intake/acq-sample/source/zeta.txt",
            ],
        )
        self.assertEqual(result["status"], "partial")

    def test_preparation_metadata_matches_exact_file_bytes(self):
        original = self.source / "guide.md"
        original.write_bytes("prima\\nseconda\\n".encode("utf-8"))
        self.write_catalog_for_directory()
        result = self.prepare()
        prepared = result["files"][0]
        self.assertEqual(prepared["sha256"], digest_file(original))
        self.assertEqual(prepared["bytes"], len(original.read_bytes()))
        self.assertEqual(prepared["line_count"], 2)

    def test_excludes_unsupported_extension_with_reason(self):
        (self.source / "picture.png").write_bytes(b"PNG")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["skipped"], [{
            "source": "intake/acq-sample/source/picture.png",
            "reason": "unsupported_extension",
        }])

    def test_excludes_file_over_per_file_limit(self):
        (self.source / "large.txt").write_bytes(b"x" * (256 * 1024 + 1))
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["skipped"][0]["reason"], "file_too_large")

    def test_file_after_per_file_exclusion_can_still_be_selected(self):
        (self.source / "a-large.txt").write_bytes(b"x" * (256 * 1024 + 1))
        (self.source / "b-small.txt").write_text("ok", encoding="utf-8")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "partial")
        self.assertEqual([item["source"].rsplit("/", 1)[-1] for item in result["files"]], [
            "b-small.txt"
        ])
        self.assertEqual(result["skipped"][0]["reason"], "file_too_large")

    def test_total_size_limit_does_not_prevent_later_smaller_file(self):
        (self.source / "a.txt").write_bytes(b"a" * (600 * 1024))
        (self.source / "b.txt").write_bytes(b"b" * (500 * 1024))
        (self.source / "c.txt").write_bytes(b"c" * (400 * 1024))
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual([item["source"].rsplit("/", 1)[-1] for item in result["files"]], [
            "a.txt", "c.txt"
        ])
        self.assertEqual(result["skipped"][0]["reason"], "total_size_limit")
        self.assertEqual(result["summary"]["total_bytes"], 1000 * 1024)

    def test_selects_at_most_one_hundred_files(self):
        for index in range(101):
            (self.source / f"{index:03}.txt").write_text(str(index), encoding="utf-8")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(len(result["files"]), 100)
        self.assertEqual(result["summary"]["files_examined"], 100)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["skipped"][-1]["reason"], "max_files_reached")

    def test_invalid_utf8_file_is_excluded(self):
        (self.source / "invalid.txt").write_bytes(b"\\xff\\xfe")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["skipped"][0]["reason"], "invalid_utf8")

    def test_nul_content_is_excluded(self):
        (self.source / "binary.txt").write_bytes(b"test\\x00data")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["skipped"][0]["reason"], "nul_byte")

    def test_valid_and_invalid_files_produce_partial_status(self):
        (self.source / "valid.md").write_text("valido", encoding="utf-8")
        (self.source / "invalid.txt").write_bytes(b"\\xff")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "partial")
        self.assertEqual(len(result["files"]), 1)
        self.assertEqual(result["skipped"][0]["reason"], "invalid_utf8")

    def test_remote_reference_is_not_fetched_or_prepared(self):
        self.write_catalog([{
            "id": "acq.sample",
            "acquisition": {
                "status": "received",
                "original": {
                    "kind": "remote_reference",
                    "uri": "https://example.org/material",
                },
            },
        }])
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertIsNone(result["material"]["sha256"])
        self.assertEqual(result["files"], [])
        self.assertEqual(result["skipped"], [])

    def test_opaque_archive_is_not_extracted(self):
        archive = self.source / "package.zip"
        archive.write_bytes(b"PK\\x03\\x04opaque")
        self.write_catalog_for_directory(kind="archive")
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["files"], [])
        self.assertEqual(archive.read_bytes(), b"PK\\x03\\x04opaque")

    def test_archive_with_text_extension_is_read_as_data_but_not_extracted(self):
        archive_named_text = self.source / "archive.md"
        archive_named_text.write_text("testo non compresso", encoding="utf-8")
        self.write_catalog_for_directory(kind="archive")
        result = self.prepare()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["files"][0]["content"], "testo non compresso")

    def test_changed_material_is_blocked_before_preparation(self):
        (self.source / "guide.md").write_text("originale", encoding="utf-8")
        self.write_catalog_for_directory()
        (self.source / "guide.md").write_text("modificato", encoding="utf-8")
        result = self.prepare()
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["files"], [])

    def test_rejects_symbolic_link_even_when_extension_is_unsupported(self):
        target = self.source / "target.bin"
        target.write_bytes(b"x")
        link = self.source / "link.bin"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Collegamenti simbolici non disponibili in questo ambiente")
        self.write_catalog_for_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["files"], [])

    def test_does_not_modify_original_or_catalog(self):
        original = self.source / "guide.md"
        original.write_text("immutabile", encoding="utf-8")
        self.write_catalog_for_directory()
        before_original = original.read_bytes()
        catalog_path = self.root / "catalog/materials.json"
        before_catalog = catalog_path.read_bytes()
        self.prepare()
        self.assertEqual(original.read_bytes(), before_original)
        self.assertEqual(catalog_path.read_bytes(), before_catalog)

    def test_does_not_accept_an_arbitrary_source_path(self):
        with self.assertRaises(TypeError):
            prepare_material(self.root, "acq.sample", source_path=self.source)

    def test_result_contains_no_absolute_paths_or_persisted_content_copy(self):
        (self.source / "guide.md").write_text("solo memoria", encoding="utf-8")
        self.write_catalog_for_directory()
        result = self.prepare()
        serialized = json.dumps(result)
        self.assertNotIn(str(self.root), serialized)
        self.assertFalse((self.root / "prepared").exists())
        self.assertEqual(result["files"][0]["content"], "solo memoria")

    def test_matches_existing_classifier_selection_and_text_order(self):
        (self.source / "zeta.md").write_text("Z", encoding="utf-8")
        (self.source / "nested").mkdir()
        (self.source / "nested" / "alpha.txt").write_text("A", encoding="utf-8")
        (self.source / "image.png").write_bytes(b"PNG")
        self.write_catalog_for_directory()
        expected_texts, expected_evidence, expected_skipped = _read_evidence(self.source, self.root)
        result = self.prepare()
        self.assertEqual(
            [(item["source"], item["content"]) for item in result["files"]],
            expected_texts,
        )
        self.assertEqual(
            [(item["source"], item["sha256"], item["bytes"]) for item in result["files"]],
            [(item["source"], item["sha256"], item["bytes"]) for item in expected_evidence],
        )
        self.assertEqual(
            [item["source"] for item in result["skipped"]],
            expected_skipped,
        )


if __name__ == "__main__":
    unittest.main()
