import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.validate_library import validate_repository
from test_validate_library import make_repo, write_json


def digest_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_directory(path):
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


class HeterogeneousIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_repo(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def register_material(self, kind, relative_path):
        source = self.root / relative_path
        checksum = digest_directory(source) if source.is_dir() else digest_file(source)
        write_json(self.root, "catalog/materials.json", {
            "catalog_version": "1.0",
            "materials": [{
                "id": "acq.sample",
                "name": "Materiale di prova",
                "acquisition": {
                    "status": "preserved",
                    "acquired_at": "2026-11-02T10:00:00Z",
                    "method": "test-fixture",
                    "original": {
                        "kind": kind,
                        "path": relative_path,
                        "sha256": checksum
                    }
                },
                "classification": {
                    "status": "classified",
                    "kind": "skill",
                    "confidence": "high",
                    "rationale": "Materiale di prova classificato come skill."
                },
                "documentation": {"status": "partial"},
                "verification": {"status": "not_verified"},
                "usability": {"status": "not_assessed"}
            }]
        })
        skills = json.loads((self.root / "catalog/skills.json").read_text(encoding="utf-8"))
        skill = skills["skills"][0]
        skill.pop("path", None)
        skill["source_record_id"] = "acq.sample"
        skill["lifecycle"] = "unverified"
        skill["selection"]["verification"] = {
            "status": "not_run",
            "evidence_refs": []
        }
        write_json(self.root, "catalog/skills.json", skills)

    def test_accepts_skill_from_single_file_without_skill_md(self):
        source = self.root / "intake/acq-sample/source"
        source.mkdir(parents=True)
        (source / "procedure.txt").write_text("Procedura originale.\n", encoding="utf-8")
        self.register_material("file", "intake/acq-sample/source/procedure.txt")
        self.assertEqual(validate_repository(self.root), [])

    def test_accepts_directory_package_without_skill_md(self):
        source = self.root / "intake/acq-folder/source"
        (source / "references").mkdir(parents=True)
        (source / "instructions.txt").write_text("Istruzioni originali.\n", encoding="utf-8")
        (source / "references/source.txt").write_text("Riferimento originale.\n", encoding="utf-8")
        self.register_material("directory", "intake/acq-folder/source")
        self.assertEqual(validate_repository(self.root), [])

    def test_accepts_archive_package_without_extracting_or_rewriting_it(self):
        source = self.root / "intake/acq-archive/source"
        source.mkdir(parents=True)
        archive = source / "package.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            bundle.writestr("instructions.txt", "Contenuto originale.\n")
        before = archive.read_bytes()
        self.register_material("archive", "intake/acq-archive/source/package.zip")
        self.assertEqual(validate_repository(self.root), [])
        self.assertEqual(archive.read_bytes(), before)

    def test_rejects_modified_preserved_original(self):
        source = self.root / "intake/acq-sample/source"
        source.mkdir(parents=True)
        original = source / "procedure.txt"
        original.write_text("Procedura originale.\n", encoding="utf-8")
        self.register_material("file", "intake/acq-sample/source/procedure.txt")
        original.write_text("Procedura alterata.\n", encoding="utf-8")
        errors = validate_repository(self.root)
        self.assertTrue(any("impronta" in error.lower() for error in errors), errors)

    def test_rejects_skill_record_linked_to_non_skill_material(self):
        source = self.root / "intake/acq-sample/source"
        source.mkdir(parents=True)
        (source / "procedure.txt").write_text("Materiale.\n", encoding="utf-8")
        self.register_material("file", "intake/acq-sample/source/procedure.txt")
        materials = json.loads((self.root / "catalog/materials.json").read_text(encoding="utf-8"))
        materials["materials"][0]["classification"]["kind"] = "resource"
        write_json(self.root, "catalog/materials.json", materials)
        errors = validate_repository(self.root)
        self.assertTrue(any("non è classificato come skill" in error.lower() for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
