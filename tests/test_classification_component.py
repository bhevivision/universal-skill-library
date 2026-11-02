import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.classify_material import analyze_material, save_proposal


class ClassificationComponentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "intake/acq-skill/source").mkdir(parents=True)
        (self.root / "catalog").mkdir()
        self.material = self.root / "intake/acq-skill/source/SKILL.md"
        self.material.write_text(
            "---\nname: report-writer\ndescription: Creates structured reports from source material.\n---\n"
            "# Report Writer\n\n## Instructions\n1. Read the source.\n2. Produce a report.\n",
            encoding="utf-8",
        )
        digest = self._digest()
        record = {
            "catalog_version": "1.0",
            "materials": [{
                "id": "acq.skill",
                "acquisition": {"status": "preserved", "original": {
                    "kind": "directory", "path": "intake/acq-skill/source",
                    "sha256": digest, "digest_algorithm": "sha256-tree-v2"
                }},
                "classification": {"status": "not_examined", "kind": "unclassified"},
                "documentation": {"status": "unknown"},
                "verification": {"status": "not_verified"},
                "usability": {"status": "not_assessed"}
            }]
        }
        (self.root / "catalog/materials.json").write_text(json.dumps(record), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_proposes_skill_with_evidence_and_original_fingerprint(self):
        result = analyze_material(self.root, "acq.skill")
        self.assertEqual(result["proposal"]["kind"], "skill")
        self.assertTrue(result["evidence"])
        self.assertEqual(result["material"]["sha256"], self._digest())

    def test_does_not_modify_material_or_material_catalog(self):
        before = self.material.read_bytes()
        catalog_before = (self.root / "catalog/materials.json").read_bytes()
        analyze_material(self.root, "acq.skill")
        self.assertEqual(self.material.read_bytes(), before)
        self.assertEqual((self.root / "catalog/materials.json").read_bytes(), catalog_before)

    def test_persists_proposal_outside_approved_catalog(self):
        result = analyze_material(self.root, "acq.skill")
        path = save_proposal(self.root, result, "proposal.test")
        self.assertTrue(path.is_file())
        self.assertFalse((self.root / "catalog/skills.json").exists())
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["status"], "pending_approval")

    def test_rejects_material_when_fingerprint_has_changed(self):
        self.material.write_text("changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            analyze_material(self.root, "acq.skill")

    def test_unknown_binary_material_is_not_guessed_or_executed(self):
        binary = self.material.parent / "payload.bin"
        binary.write_bytes(b"\x00\xff\x00")
        result = analyze_material(self.root, "acq.skill")
        self.assertIn(result["proposal"]["kind"], {"skill", "unclassified"})
        self.assertTrue(result["limits"])

    def _digest(self):
        digest = hashlib.sha256()
        for item in sorted(self.material.parent.rglob("*"), key=lambda entry: entry.relative_to(self.material.parent).as_posix()):
            relative = item.relative_to(self.material.parent).as_posix().encode("utf-8")
            if item.is_dir():
                digest.update(b"D\0" + relative + b"\0")
            elif item.is_file():
                digest.update(b"F\0" + relative + b"\0")
                digest.update(item.read_bytes())
                digest.update(b"\0")
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
