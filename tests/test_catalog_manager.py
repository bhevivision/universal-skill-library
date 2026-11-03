import json
import tempfile
import unittest
from pathlib import Path
from shutil import copytree

from scripts.catalog_manager import CatalogError, get_entry, list_entries, put_entry, remove_entry, search_entries


class CatalogManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1] / "schemas"
        copytree(source, self.root / "schemas")
        skill_source = Path(__file__).resolve().parents[1] / "skills"
        copytree(skill_source, self.root / "skills")
        (self.root / "catalog").mkdir()
        for name, collection in (
            ("skills", "skills"), ("capabilities", "capabilities"),
            ("implementations", "implementations"), ("materials", "materials")
        ):
            (self.root / "catalog" / f"{name}.json").write_text(
                json.dumps({"catalog_version": "1.0", collection: []}), encoding="utf-8"
            )

    def tearDown(self):
        self.temp.cleanup()

    def capability(self, entry_id="cap.read"):
        return {
            "id": entry_id,
            "name": "Lettura documenti",
            "description": "Legge documenti testuali.",
            "category": "documenti",
            "expected_result": "Contenuto estratto.",
            "verification_criteria": ["Il testo è recuperabile."],
            "status": "draft"
        }

    def test_add_list_show_and_search(self):
        put_entry(self.root, "capabilities", self.capability())
        self.assertEqual(list_entries(self.root, "capabilities")[0]["id"], "cap.read")
        self.assertEqual(get_entry(self.root, "capabilities", "cap.read")["name"], "Lettura documenti")
        self.assertEqual(len(search_entries(self.root, "capabilities", "documenti")), 1)

    def test_duplicate_add_is_rejected(self):
        put_entry(self.root, "capabilities", self.capability())
        with self.assertRaises(CatalogError):
            put_entry(self.root, "capabilities", self.capability())

    def test_update_replaces_existing_entry(self):
        put_entry(self.root, "capabilities", self.capability())
        updated = self.capability()
        updated["name"] = "Lettura e analisi documenti"
        put_entry(self.root, "capabilities", updated, replace=True)
        self.assertEqual(get_entry(self.root, "capabilities", "cap.read")["name"],
                         "Lettura e analisi documenti")

    def test_remove_deletes_entry(self):
        put_entry(self.root, "capabilities", self.capability())
        remove_entry(self.root, "capabilities", "cap.read")
        self.assertEqual(list_entries(self.root, "capabilities"), [])

    def test_invalid_entry_is_not_written(self):
        with self.assertRaises(CatalogError):
            put_entry(self.root, "capabilities", {"id": "bad"})
        self.assertEqual(list_entries(self.root, "capabilities"), [])



    def material(self, entry_id="source.example", *, kind="resource", license_record=None):
        entry = {
            "id": entry_id,
            "acquisition": {
                "status": "received",
                "acquired_at": "2026-11-03T20:00:00Z",
                "method": "remote_reference",
                "original": {"kind": "remote_reference", "uri": "https://example.org/source"}
            },
            "classification": {"status": "classified", "kind": kind},
            "documentation": {"status": "partial"},
            "verification": {"status": "not_verified"},
            "usability": {"status": "not_assessed"}
        }
        if license_record is not None:
            entry["license"] = license_record
        return entry

    def skill(self, *, source_material_ids=None, source_record_id=None, verification=None):
        catalog = json.loads((Path(__file__).resolve().parents[1] / "catalog" / "skills.json").read_text(encoding="utf-8"))
        entry = json.loads(json.dumps(catalog["skills"][0]))
        entry["id"] = "test.skill"
        entry["path"] = "skills/resource-discovery-assessment/SKILL.md"
        entry["capability_ids"] = ["cap.read"]
        entry["selection"]["verification"] = {"status": "not_run", "evidence_refs": []}
        if source_material_ids is not None:
            entry["source_material_ids"] = source_material_ids
        else:
            entry.pop("source_material_ids", None)
        entry.pop("source_record_id", None)
        if source_record_id is not None:
            entry["source_record_id"] = source_record_id
        if verification is not None:
            entry["selection"]["verification"] = verification
        return entry

    def add_skill_prerequisites(self, source_ids=()):
        put_entry(self.root, "capabilities", self.capability())
        for source_id in source_ids:
            put_entry(self.root, "materials", self.material(source_id))

    def test_add_skill_with_valid_source_materials(self):
        self.add_skill_prerequisites(["source.one", "source.two"])
        entry = self.skill(source_material_ids=["source.one", "source.two"])
        put_entry(self.root, "skills", entry)
        self.assertEqual(get_entry(self.root, "skills", "test.skill")["source_material_ids"],
                         ["source.one", "source.two"])

    def test_reject_skill_with_missing_source_material(self):
        self.add_skill_prerequisites()
        with self.assertRaisesRegex(CatalogError, "Materiale sorgente inesistente"):
            put_entry(self.root, "skills", self.skill(source_material_ids=["source.missing"]))
        self.assertEqual(list_entries(self.root, "skills"), [])

    def test_reject_skill_source_record_that_is_not_a_skill(self):
        put_entry(self.root, "capabilities", self.capability())
        put_entry(self.root, "materials", self.material("source.document", kind="resource"))
        with self.assertRaisesRegex(CatalogError, "deve essere una skill classificata"):
            put_entry(self.root, "skills", self.skill(source_record_id="source.document"))
        self.assertEqual(list_entries(self.root, "skills"), [])

    def test_reject_material_with_missing_reviewed_license_evidence(self):
        license_record = {
            "status": "identified",
            "identifier": "MIT",
            "source_uri": "https://example.org/LICENSE",
            "source_revision": "a" * 40,
            "file_path": "LICENSE",
            "review_status": "reviewed",
            "reviewed_at": "2026-11-03T20:00:00Z",
            "evidence_refs": ["tests/evidence/missing-license-proof.json"],
            "obligations": ["Conservare il testo della licenza."]
        }
        with self.assertRaisesRegex(CatalogError, "prova non trovata"):
            put_entry(self.root, "materials", self.material("source.licensed", license_record=license_record))
        self.assertEqual(list_entries(self.root, "materials"), [])

    def test_reject_skill_with_missing_verification_evidence(self):
        self.add_skill_prerequisites(["source.one"])
        verification = {
            "status": "passed",
            "last_checked": "2026-11-03T20:00:00Z",
            "evidence_refs": ["tests/evidence/missing-skill-proof.json"]
        }
        with self.assertRaisesRegex(CatalogError, "prova non trovata"):
            put_entry(self.root, "skills", self.skill(source_material_ids=["source.one"], verification=verification))
        self.assertEqual(list_entries(self.root, "skills"), [])

    def test_prevent_removing_material_referenced_by_source_material_ids(self):
        self.add_skill_prerequisites(["source.keep"])
        put_entry(self.root, "skills", self.skill(source_material_ids=["source.keep"]))
        with self.assertRaisesRegex(CatalogError, "fonte di una skill"):
            remove_entry(self.root, "materials", "source.keep")
        self.assertEqual(get_entry(self.root, "materials", "source.keep")["id"], "source.keep")

    def test_accept_material_with_matching_license_evidence(self):
        proof_dir = self.root / "tests" / "evidence"
        proof_dir.mkdir(parents=True)
        proof = {
            "id": "proof.source.valid.license",
            "subject": "material.source.valid.license",
            "result": "passed",
            "tested_at": "2026-11-03T20:00:00Z",
            "command": "Verifica licenza della fonte di prova.",
            "summary": "La licenza MIT è stata identificata nella fonte fissata."
        }
        (proof_dir / "license-valid.json").write_text(json.dumps(proof), encoding="utf-8")
        license_record = {
            "status": "identified",
            "identifier": "MIT",
            "source_uri": "https://example.org/LICENSE",
            "source_revision": "a" * 40,
            "file_path": "LICENSE",
            "review_status": "reviewed",
            "reviewed_at": "2026-11-03T20:00:00Z",
            "evidence_refs": ["tests/evidence/license-valid.json"],
            "obligations": ["Conservare il testo della licenza."]
        }
        put_entry(self.root, "materials", self.material("source.valid", license_record=license_record))
        self.assertEqual(get_entry(self.root, "materials", "source.valid")["license"]["identifier"], "MIT")

if __name__ == "__main__":
    unittest.main()
