import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.semantic_evidence_integrity import validate_semantic_proposal


def build_fixture(root):
    material_dir = root / "intake/acq-example/source"
    material_dir.mkdir(parents=True)
    examined = material_dir / "SKILL.md"
    examined.write_text("# Instructions\nUse the supplied documents.\n", encoding="utf-8")
    original_hash = hashlib.sha256(examined.read_bytes()).hexdigest()
    record = {
        "id": "acq.example",
        "acquisition": {
            "status": "preserved",
            "acquired_at": "2026-11-02T10:00:00Z",
            "method": "copy",
            "original": {
                "kind": "file",
                "path": "intake/acq-example/source/SKILL.md",
                "sha256": original_hash,
                "digest_algorithm": "sha256-file-v1"
            }
        },
        "classification": {"status": "not_examined", "kind": "unclassified"},
        "documentation": {"status": "unknown"},
        "verification": {"status": "not_verified"},
        "usability": {"status": "not_assessed"}
    }
    catalog_path = root / "catalog/materials.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps({"catalog_version": "1.0", "materials": [record]}, indent=2) + "\n", encoding="utf-8")
    catalog_hash = hashlib.sha256(catalog_path.read_bytes()).hexdigest()
    proposal = {
        "schema_version": "1.0",
        "proposal_id": "sem.example",
        "created_at": "2026-11-02T10:00:00Z",
        "status": "completed",
        "material": {"id": "acq.example", "sha256": original_hash, "original_kind": "file"},
        "classification": {
            "kind": "skill", "confidence": "medium",
            "rationale": "Istruzioni operative presenti.",
            "summary": "Materiale operativo.", "evidence_refs": ["ev.instructions"]
        },
        "capabilities": [{
            "id": "cap.example", "name": "Esecuzione istruzioni",
            "description": "Segue istruzioni documentate.", "certainty": "declared",
            "evidence_refs": ["ev.instructions"]
        }],
        "interfaces": {"inputs": [], "outputs": [], "usage_conditions": []},
        "dependencies": [],
        "tools_and_platforms": [],
        "evidence": [
            {"id": "ev.instructions", "source": "intake/acq-example/source/SKILL.md",
             "sha256": original_hash, "kind": "text_file"},
            {"id": "ev.catalog", "source": "catalog/materials.json",
             "sha256": catalog_hash, "kind": "metadata"}
        ],
        "missing_references": [], "contradictions": [], "risks": [],
        "unknowns": [], "limits": [],
        "analyzer": {
            "id": "test-analyzer", "version": "1.0", "provider": "local",
            "external_data_authorized": False,
            "input_sha256": "d" * 64, "output_sha256": "e" * 64
        }
    }
    return proposal, examined, catalog_path


class SemanticEvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proposal, self.examined, self.catalog = build_fixture(self.root)

    def test_accepts_proposal_with_real_file_and_catalog_evidence(self):
        self.assertTrue(validate_semantic_proposal(self.root, self.proposal))

    def test_rejects_reference_to_missing_evidence_id(self):
        self.proposal["classification"]["evidence_refs"] = ["ev.missing"]
        with self.assertRaisesRegex(ValueError, "riferimento.*inesistente"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_duplicate_evidence_identifiers(self):
        duplicate = dict(self.proposal["evidence"][0])
        duplicate["source"] = "intake/acq-example/source/other.md"
        self.proposal["evidence"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "identificativo.*duplicato"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_file_hash_that_does_not_match_examined_file(self):
        self.proposal["evidence"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "impronta.*non corrisponde"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_material_changed_after_proposal_creation(self):
        self.examined.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "materiale.*modificato"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_evidence_outside_the_acquired_material_directory(self):
        outside = self.root / "intake/acq-example/other.md"
        outside.write_text("not part of original", encoding="utf-8")
        self.proposal["evidence"][0]["source"] = "intake/acq-example/other.md"
        self.proposal["evidence"][0]["sha256"] = hashlib.sha256(outside.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, "fuori dal materiale"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_path_traversal(self):
        self.proposal["evidence"][0]["source"] = "intake/acq-example/source/../../../../outside.md"
        with self.assertRaises(ValueError):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_catalog_evidence_with_wrong_fingerprint(self):
        self.proposal["evidence"][1]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "impronta.*catalogo"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_duplicate_evidence_ids_even_if_entries_differ(self):
        self.proposal["evidence"].append({
            "id": "ev.instructions", "source": "intake/acq-example/source/SKILL.md",
            "sha256": self.proposal["evidence"][0]["sha256"], "kind": "text_file"
        })
        with self.assertRaisesRegex(ValueError, "identificativo.*duplicato"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_reference_to_material_with_wrong_original_fingerprint(self):
        self.proposal["material"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "impronta.*materiale"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_rejects_symlink_evidence(self):
        target = self.root / "outside.md"
        target.write_text("outside", encoding="utf-8")
        link = self.examined.parent / "linked.md"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Collegamenti simbolici non disponibili in questo ambiente")
        self.proposal["evidence"][0]["source"] = "intake/acq-example/source/linked.md"
        self.proposal["evidence"][0]["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, "collegamento simbolico"):
            validate_semantic_proposal(self.root, self.proposal)


    def test_rejects_line_range_outside_examined_file(self):
        self.proposal["evidence"][0]["location"] = {"start_line": 1, "end_line": 99}
        with self.assertRaisesRegex(ValueError, "Intervallo di righe"):
            validate_semantic_proposal(self.root, self.proposal)

    def test_accepts_line_range_present_in_examined_file(self):
        self.proposal["evidence"][0]["location"] = {"start_line": 1, "end_line": 2}
        self.assertTrue(validate_semantic_proposal(self.root, self.proposal))


if __name__ == "__main__":
    unittest.main()
