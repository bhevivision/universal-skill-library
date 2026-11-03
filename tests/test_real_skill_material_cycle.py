import tempfile
import unittest
from pathlib import Path

from scripts.acquire_material import acquire_material
from scripts.classify_material import analyze_material
from scripts.material_preparer import prepare_material
from test_validate_library import make_repo


class ExistingSkillMaterialCycleTests(unittest.TestCase):
    """Esercita materiali reali già presenti nel repository, senza promuoverli automaticamente."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "library"
        self.root.mkdir()
        make_repo(self.root)
        self.source_root = Path(__file__).resolve().parents[1] / "personalizzazione"

    def tearDown(self):
        self.temp.cleanup()

    def test_acquire_prepare_and_classify_existing_instruction_materials(self):
        candidates = (
            "UNLAZY-skill.md",
            "archivista-skill.md",
            "find-skill.md",
        )
        for index, filename in enumerate(candidates, start=1):
            with self.subTest(filename=filename):
                source = self.source_root / filename
                self.assertTrue(source.is_file(), f"Materiale campione assente: {filename}")
                material_id = f"acq.real-skill-{index}"
                record = acquire_material(self.root, source, material_id)
                self.assertEqual(record["acquisition"]["status"], "preserved")

                prepared = prepare_material(self.root, material_id)
                self.assertIn(prepared["status"], {"completed", "partial"})
                self.assertGreater(prepared["summary"]["files_examined"], 0)
                self.assertTrue(prepared["files"])

                proposal = analyze_material(self.root, material_id)
                self.assertEqual(proposal["status"], "pending_approval")
                self.assertEqual(proposal["material"]["id"], material_id)
                self.assertTrue(proposal["evidence"])
                self.assertTrue(any(
                    item.get("type") == "text_file" and item.get("sha256")
                    for item in proposal["evidence"]
                ))

        # L'acquisizione conserva i tre originali come record separati.
        import json
        catalog = json.loads((self.root / "catalog/materials.json").read_text(encoding="utf-8"))
        self.assertEqual(len(catalog["materials"]), 3)
        self.assertEqual(
            {item["id"] for item in catalog["materials"]},
            {"acq.real-skill-1", "acq.real-skill-2", "acq.real-skill-3"},
        )


if __name__ == "__main__":
    unittest.main()
