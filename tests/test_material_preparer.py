import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.classify_material import _read_evidence
from scripts.material_integrity import verify_material as real_verify_material
from scripts.material_preparer import prepare_material

TEXT_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".rst", ".json", ".yaml", ".yml",
    ".toml", ".py", ".js", ".ts", ".sh", ".ps1", ".bat", ".xml",
    ".html", ".css",
}
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 1024 * 1024
MAX_FILES = 100


def digest_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_directory(path):
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*"), key=lambda entry: entry.relative_to(path).as_posix()):
        relative = item.relative_to(path).as_posix().encode("utf-8")
        if item.is_symlink():
            raise AssertionError("Il fixture non può contenere collegamenti simbolici.")
        if item.is_dir():
            digest.update(b"D\0" + relative + b"\0")
        elif item.is_file():
            digest.update(b"F\0" + relative + b"\0")
            digest.update(item.read_bytes())
            digest.update(b"\0")
    return digest.hexdigest()


class MaterialPreparerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "catalog").mkdir()
        self.source = self.root / "intake/acq-sample/source"
        self.source.mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def write_catalog(self, materials):
        (self.root / "catalog/materials.json").write_text(
            json.dumps({"catalog_version": "1.0", "materials": materials}), encoding="utf-8"
        )

    def register_directory(self, *, kind="directory", state="preserved"):
        self.write_catalog([{
            "id": "acq.sample",
            "acquisition": {"status": state, "original": {
                "kind": kind, "path": "intake/acq-sample/source",
                "sha256": digest_directory(self.source), "digest_algorithm": "sha256-tree-v2",
            }},
        }])

    def register_file(self, path, *, state="preserved", kind="file"):
        self.write_catalog([{
            "id": "acq.sample",
            "acquisition": {"status": state, "original": {
                "kind": kind, "path": path.relative_to(self.root).as_posix(),
                "sha256": digest_file(path), "digest_algorithm": "sha256-file-v1",
            }},
        }])

    def prepare(self, **kwargs):
        return prepare_material(self.root, "acq.sample", **kwargs)

    def assert_error_result(self, result, status):
        self.assertEqual(result["status"], status)
        self.assertEqual(result["files"], [])
        self.assertEqual(result["summary"]["total_bytes"], 0)
        self.assertTrue(result["problems"])

    # Identità e servizio d'integrità

    def test_001_single_file_material_is_prepared(self):
        path = self.source / "guide.md"
        path.write_text("# Guida\nTesto.\n", encoding="utf-8")
        self.register_file(path)
        result = self.prepare()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["files"][0]["content"], "# Guida\nTesto.\n")

    def test_002_missing_material_is_blocked(self):
        self.register_directory()
        self.write_catalog([])
        self.assert_error_result(self.prepare(), "blocked")

    def test_003_duplicate_material_id_is_blocked(self):
        self.register_directory()
        record = json.loads((self.root / "catalog/materials.json").read_text())["materials"][0]
        self.write_catalog([record, record])
        self.assert_error_result(self.prepare(), "blocked")

    def test_004_local_material_must_be_preserved(self):
        (self.source / "a.txt").write_text("x", encoding="utf-8")
        self.register_directory(state="received")
        self.assert_error_result(self.prepare(), "blocked")

    def test_005_integrity_blocked_is_mapped_to_blocked(self):
        self.register_directory()
        result = {"status": "blocked", "problems": [{"code": "DIGEST_MISMATCH", "message": "alterato"}]}
        with patch("scripts.material_preparer.verify_material", return_value=result):
            prepared = self.prepare()
        self.assert_error_result(prepared, "blocked")
        self.assertEqual(prepared["problems"][0]["code"], "DIGEST_MISMATCH")

    def test_006_integrity_failed_is_mapped_to_failed(self):
        self.register_directory()
        result = {"status": "failed", "problems": [{"code": "IO_ERROR", "message": "errore"}]}
        with patch("scripts.material_preparer.verify_material", return_value=result):
            self.assert_error_result(self.prepare(), "failed")

    def test_007_uses_shared_integrity_service_at_start_and_end(self):
        (self.source / "a.txt").write_text("x", encoding="utf-8")
        self.register_directory()
        with patch("scripts.material_preparer.verify_material", wraps=real_verify_material) as verify:
            self.prepare()
        self.assertGreaterEqual(verify.call_count, 2)

    def test_008_does_not_accept_arbitrary_source_path(self):
        self.register_directory()
        with self.assertRaises(TypeError):
            prepare_material(self.root, "acq.sample", source_path=self.source)

    def test_009_changed_material_before_preparation_is_blocked(self):
        path = self.source / "a.txt"
        path.write_text("prima", encoding="utf-8")
        self.register_directory()
        path.write_text("dopo", encoding="utf-8")
        self.assert_error_result(self.prepare(), "blocked")

    # Estensioni, inventario e ordinamento

    def test_010_accepts_all_contract_extensions(self):
        for index, extension in enumerate(sorted(TEXT_EXTENSIONS)):
            (self.source / f"file-{index:02}{extension}").write_text("x", encoding="utf-8")
        self.register_directory()
        self.assertEqual(len(self.prepare()["files"]), len(TEXT_EXTENSIONS))

    def test_011_extension_matching_is_case_insensitive(self):
        (self.source / "GUIDE.MD").write_text("testo", encoding="utf-8")
        self.register_directory()
        self.assertEqual(self.prepare()["files"][0]["content"], "testo")

    def test_012_unsupported_extension_is_reported(self):
        (self.source / "picture.png").write_bytes(b"PNG")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["skipped"][0]["reason"], "unsupported_extension")

    def test_013_hidden_files_are_included(self):
        (self.source / ".hidden.txt").write_text("nascosto", encoding="utf-8")
        self.register_directory()
        self.assertTrue(self.prepare()["files"][0]["source"].endswith(".hidden.txt"))

    def test_014_empty_directories_are_not_files(self):
        (self.source / "empty").mkdir()
        self.register_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["summary"]["files_skipped"], 0)

    def test_015_recursive_candidates_keep_path_sorted_order(self):
        (self.source / "z.txt").write_text("Z", encoding="utf-8")
        (self.source / "nested").mkdir()
        (self.source / "nested/a.md").write_text("A", encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertEqual([x["content"] for x in result["files"]], ["A", "Z"])

    # Limiti e ordine dei controlli

    def test_016_exact_per_file_limit_is_accepted(self):
        (self.source / "exact.txt").write_bytes(b"x" * MAX_FILE_BYTES)
        self.register_directory()
        self.assertEqual(self.prepare()["files"][0]["bytes"], MAX_FILE_BYTES)

    def test_017_file_over_per_file_limit_is_excluded(self):
        (self.source / "large.txt").write_bytes(b"x" * (MAX_FILE_BYTES + 1))
        self.register_directory()
        self.assertEqual(self.prepare()["skipped"][0]["reason"], "file_too_large")

    def test_018_oversized_file_does_not_consume_selection_slot(self):
        (self.source / "a-large.txt").write_bytes(b"x" * (MAX_FILE_BYTES + 1))
        (self.source / "b-small.txt").write_text("ok", encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertEqual([x["content"] for x in result["files"]], ["ok"])
        self.assertEqual(result["skipped"][0]["reason"], "file_too_large")

    def test_019_exact_total_limit_is_accepted(self):
        for index in range(4):
            (self.source / f"{index}.txt").write_bytes(bytes([65 + index]) * MAX_FILE_BYTES)
        self.register_directory()
        self.assertEqual(self.prepare()["summary"]["total_bytes"], MAX_TOTAL_BYTES)

    def test_020_total_size_limit_excludes_overflow(self):
        for index in range(4):
            (self.source / f"{index}.txt").write_bytes(b"a" * MAX_FILE_BYTES)
        (self.source / "4.txt").write_bytes(b"b")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(result["skipped"][0]["reason"], "total_size_limit")

    def test_021_total_size_exclusion_does_not_prevent_later_small_file(self):
        for index in range(3):
            (self.source / f"{index}.txt").write_bytes(b"a" * MAX_FILE_BYTES)
        (self.source / "3.txt").write_bytes(b"b" * (132 * 1024))
        (self.source / "4.txt").write_bytes(b"c" * (200 * 1024))
        (self.source / "5.txt").write_bytes(b"d" * (100 * 1024))
        self.register_directory()
        result = self.prepare()
        self.assertEqual([x["source"].rsplit("/", 1)[-1] for x in result["files"]], ["0.txt", "1.txt", "2.txt", "3.txt", "5.txt"])
        self.assertEqual(result["summary"]["total_bytes"], 1000 * 1024)

    def test_022_maximum_one_hundred_selected_files(self):
        for index in range(101):
            (self.source / f"{index:03}.txt").write_text(str(index), encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(len(result["files"]), 100)
        self.assertEqual(result["skipped"][-1]["reason"], "max_files_reached")

    def test_023_invalid_selected_file_still_consumes_one_of_one_hundred_slots(self):
        for index in range(100):
            (self.source / f"{index:03}.txt").write_bytes(b"\xff" if index == 0 else str(index).encode())
        (self.source / "100.txt").write_text("101", encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(len(result["files"]), 99)
        self.assertTrue(any(x["source"].endswith("/100.txt") and x["reason"] == "max_files_reached" for x in result["skipped"]))

    # Lettura, codifica e metadati

    def test_024_invalid_utf8_is_excluded(self):
        (self.source / "invalid.txt").write_bytes(b"\xff\xfe")
        self.register_directory()
        self.assertEqual(self.prepare()["skipped"][0]["reason"], "invalid_utf8")

    def test_025_actual_nul_byte_is_excluded(self):
        (self.source / "binary.txt").write_bytes(b"test\x00data")
        self.register_directory()
        self.assertEqual(self.prepare()["skipped"][0]["reason"], "nul_byte")

    def test_026_utf8_text_is_preserved_without_normalization(self):
        text = "città — naïve\n第二行\n"
        (self.source / "unicode.md").write_bytes(text.encode("utf-8"))
        self.register_directory()
        self.assertEqual(self.prepare()["files"][0]["content"], text)

    def test_027_line_count_uses_splitlines(self):
        text = "prima\r\nseconda\u2028terza\n"
        (self.source / "lines.txt").write_bytes(text.encode("utf-8"))
        self.register_directory()
        self.assertEqual(self.prepare()["files"][0]["line_count"], len(text.splitlines()))

    def test_028_digest_and_size_match_exact_bytes(self):
        path = self.source / "exact.txt"
        raw = "à\nb".encode("utf-8")
        path.write_bytes(raw)
        self.register_directory()
        item = self.prepare()["files"][0]
        self.assertEqual(item["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(item["bytes"], len(raw))

    def test_029_read_error_is_recoverable_and_other_files_continue(self):
        (self.source / "a.txt").write_text("non leggibile", encoding="utf-8")
        (self.source / "b.txt").write_text("leggibile", encoding="utf-8")
        self.register_directory()
        original_read_bytes = Path.read_bytes
        def controlled_read(path, *args, **kwargs):
            if path.name == "a.txt":
                raise PermissionError("negato")
            return original_read_bytes(path, *args, **kwargs)
        with patch.object(Path, "read_bytes", controlled_read):
            result = self.prepare()
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["skipped"][0]["reason"], "read_error")
        self.assertEqual([x["content"] for x in result["files"]], ["leggibile"])

    def test_030_invalid_file_does_not_prevent_later_valid_file(self):
        (self.source / "a.txt").write_bytes(b"\xff")
        (self.source / "b.txt").write_text("valido", encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["files"][0]["content"], "valido")

    # Sicurezza e controllo finale

    def test_031_symlink_with_unsupported_extension_blocks(self):
        target = self.source / "target.bin"
        target.write_bytes(b"x")
        try:
            (self.source / "link.bin").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Collegamenti simbolici non disponibili.")
        self.register_directory()
        self.assert_error_result(self.prepare(), "blocked")

    def test_032_symlink_blocks_even_after_a_valid_file_was_read(self):
        (self.source / "a.txt").write_text("valido", encoding="utf-8")
        target = self.source / "target.bin"
        target.write_bytes(b"x")
        try:
            (self.source / "z-link.bin").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Collegamenti simbolici non disponibili.")
        self.register_directory()
        self.assert_error_result(self.prepare(), "blocked")

    def test_033_original_and_catalog_are_not_modified(self):
        path = self.source / "guide.md"
        path.write_text("immutabile", encoding="utf-8")
        self.register_directory()
        original_before = path.read_bytes()
        catalog_path = self.root / "catalog/materials.json"
        catalog_before = catalog_path.read_bytes()
        self.prepare()
        self.assertEqual(path.read_bytes(), original_before)
        self.assertEqual(catalog_path.read_bytes(), catalog_before)

    def test_034_no_absolute_paths_or_persisted_content_copy(self):
        (self.source / "guide.md").write_text("solo memoria", encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertNotIn(str(self.root), json.dumps(result))
        self.assertFalse((self.root / "prepared").exists())

    def test_035_final_integrity_check_runs_even_when_no_file_is_accepted(self):
        (self.source / "image.png").write_bytes(b"PNG")
        self.register_directory()
        with patch("scripts.material_preparer.verify_material", wraps=real_verify_material) as verify:
            self.prepare()
        self.assertGreaterEqual(verify.call_count, 2)

    def test_036_change_between_initial_and_final_check_blocks_result(self):
        path = self.source / "guide.md"
        path.write_text("prima", encoding="utf-8")
        self.register_directory()
        calls = {"count": 0}
        def verify_then_change(root, material_id, *args, **kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                return real_verify_material(root, material_id, *args, **kwargs)
            path.write_text("modificato durante la preparazione", encoding="utf-8")
            return real_verify_material(root, material_id, *args, **kwargs)
        with patch("scripts.material_preparer.verify_material", side_effect=verify_then_change):
            self.assert_error_result(self.prepare(), "blocked")

    def test_037_failed_final_check_discards_prepared_content(self):
        (self.source / "guide.md").write_text("contenuto", encoding="utf-8")
        self.register_directory()
        initial = real_verify_material(self.root, "acq.sample")
        final = dict(initial)
        final["status"] = "failed"
        final["problems"] = [{"code": "IO_ERROR", "message": "errore finale"}]
        with patch("scripts.material_preparer.verify_material", side_effect=[initial, final]):
            self.assert_error_result(self.prepare(), "failed")

    # Remoti, archivi e materiali eterogenei

    def test_038_remote_reference_is_never_prepared(self):
        self.write_catalog([{
            "id": "acq.sample",
            "acquisition": {"status": "received", "original": {
                "kind": "remote_reference", "uri": "https://example.org/material"
            }},
        }])
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertIsNone(result["material"]["sha256"])
        self.assertEqual(result["files"], [])
        self.assertEqual(result["skipped"], [])

    def test_039_valid_zip_is_not_extracted(self):
        archive = self.source / "package.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("guide.txt", "non estrarre")
        before = archive.read_bytes()
        self.register_file(archive, kind="archive")
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(archive.read_bytes(), before)
        self.assertFalse((self.source / "guide.txt").exists())

    def test_040_archive_with_text_extension_is_read_as_data_only(self):
        path = self.source / "opaque.md"
        path.write_text("dato opaco", encoding="utf-8")
        self.register_file(path, kind="archive")
        self.assertEqual(self.prepare()["files"][0]["content"], "dato opaco")

    def test_041_unknown_kind_uses_normal_selection_rules(self):
        (self.source / "note.txt").write_text("testo", encoding="utf-8")
        self.register_directory(kind="unknown")
        self.assertEqual(self.prepare()["files"][0]["content"], "testo")

    # Stati, conteggi e forma del risultato

    def test_042_completed_has_no_skipped_files(self):
        (self.source / "a.txt").write_text("A", encoding="utf-8")
        (self.source / "b.md").write_text("B", encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["summary"]["files_examined"], 2)
        self.assertEqual(result["summary"]["files_skipped"], 0)

    def test_043_partial_has_accepted_and_skipped_files(self):
        (self.source / "a.txt").write_text("A", encoding="utf-8")
        (self.source / "b.png").write_bytes(b"PNG")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["summary"]["files_examined"], 1)
        self.assertEqual(result["summary"]["files_skipped"], 1)

    def test_044_not_available_when_every_candidate_is_unsupported(self):
        (self.source / "image.png").write_bytes(b"PNG")
        self.register_directory()
        result = self.prepare()
        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["files"], [])

    def test_045_summary_counts_only_accepted_and_skipped_regular_files(self):
        (self.source / "a.txt").write_text("abc", encoding="utf-8")
        (self.source / "b.txt").write_bytes(b"\xff")
        (self.source / "c.png").write_bytes(b"PNG")
        self.register_directory()
        self.assertEqual(self.prepare()["summary"], {
            "files_examined": 1, "files_skipped": 2, "total_bytes": 3
        })

    def test_046_skipped_entries_do_not_contain_content_or_excerpt(self):
        (self.source / "secret.bin").write_bytes(b"SECRET_CONTENT")
        self.register_directory()
        result = self.prepare()
        self.assertNotIn("SECRET_CONTENT", json.dumps(result["skipped"]))
        self.assertNotIn("content", result["skipped"][0])
        self.assertNotIn("excerpt", result["skipped"][0])

    def test_047_sources_are_relative_posix_paths_under_intake(self):
        (self.source / "nested").mkdir()
        (self.source / "nested/note.txt").write_text("x", encoding="utf-8")
        self.register_directory()
        source = self.prepare()["files"][0]["source"]
        self.assertTrue(source.startswith("intake/"))
        self.assertNotIn("\\", source)
        self.assertFalse(Path(source).is_absolute())

    def test_048_result_has_all_required_top_level_fields(self):
        (self.source / "note.txt").write_text("x", encoding="utf-8")
        self.register_directory()
        result = self.prepare()
        self.assertTrue({
            "schema_version", "status", "material", "profile", "files",
            "skipped", "summary", "problems",
        }.issubset(result))

    def test_049_detected_inventory_error_fails_without_partial_contents(self):
        (self.source / "guide.md").write_text("testo", encoding="utf-8")
        self.register_directory()
        original_rglob = Path.rglob
        calls = {"count": 0}
        def fail_during_inventory(path, pattern):
            if path == self.source:
                calls["count"] += 1
                # Le prime due scansioni appartengono alla verifica d'integrità
                # iniziale; la successiva è l'inventario del preparatore.
                if calls["count"] == 3:
                    raise PermissionError("inventario non accessibile")
            return original_rglob(path, pattern)
        with patch.object(Path, "rglob", fail_during_inventory):
            self.assert_error_result(self.prepare(), "failed")

    # Parità osservabile con il classificatore

    def test_050_matches_classifier_paths_text_and_evidence(self):
        (self.source / "zeta.md").write_text("Z", encoding="utf-8")
        (self.source / "nested").mkdir()
        (self.source / "nested/alpha.txt").write_text("A", encoding="utf-8")
        (self.source / "image.png").write_bytes(b"PNG")
        self.register_directory()
        expected_texts, expected_evidence, expected_skipped = _read_evidence(self.source, self.root)
        result = self.prepare()
        self.assertEqual([(x["source"], x["content"]) for x in result["files"]], expected_texts)
        self.assertEqual(
            [(x["source"], x["sha256"], x["bytes"]) for x in result["files"]],
            [(x["source"], x["sha256"], x["bytes"]) for x in expected_evidence],
        )
        self.assertEqual([x["source"] for x in result["skipped"]], expected_skipped)

    def test_051_classifier_heuristic_remains_unchanged(self):
        from scripts.classify_material import _propose
        texts = [("intake/a/SKILL.md", "---\nname: x\ndescription: y\n---\n# Instructions\n")]
        self.assertEqual(_propose(texts, "directory")[0], "skill")


if __name__ == "__main__":
    unittest.main()
