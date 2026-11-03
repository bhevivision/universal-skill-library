import hashlib
import json
import os
import shutil
import socket
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts.classification_approval import approve_proposal, reject_proposal


class ClassificationApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "intake/acq-example/source").mkdir(parents=True)
        (self.root / "catalog").mkdir()
        (self.root / "proposals").mkdir()
        (self.root / "schemas").mkdir()
        schema_source = Path(__file__).resolve().parents[1] / "schemas/classification-proposal.schema.json"
        shutil.copyfile(schema_source, self.root / "schemas/classification-proposal.schema.json")
        self.original = self.root / "intake/acq-example/source/material.md"
        self.original.write_text("# Example skill\n\n## Instructions\nDo the work.\n", encoding="utf-8")
        digest = hashlib.sha256(self.original.read_bytes()).hexdigest()
        self.digest = digest
        catalog = {
            "catalog_version": "1.0",
            "materials": [{
                "id": "acq.example",
                "acquisition": {"status": "preserved", "original": {
                    "kind": "file",
                    "path": "intake/acq-example/source/material.md",
                    "sha256": digest,
                    "digest_algorithm": "sha256-file-v1"
                }},
                "classification": {"status": "not_examined", "kind": "unclassified"}
            }]
        }
        (self.root / "catalog/materials.json").write_text(json.dumps(catalog), encoding="utf-8")
        (self.root / "catalog/skills.json").write_text(
            json.dumps({"catalog_version": "1.0", "skills": []}), encoding="utf-8"
        )
        self.proposal = {
            "proposal_schema_version": "1.0",
            "proposal_id": "class.example",
            "created_at": "2026-11-02T10:00:00Z",
            "status": "pending_approval",
            "material": {"id": "acq.example", "sha256": digest, "original_kind": "file"},
            "proposal": {"kind": "skill", "confidence": "medium", "rationale": "Metadati e istruzioni rilevati."},
            "evidence": [{"source": "catalog/materials.json", "type": "identity", "material_id": "acq.example", "sha256": digest}, {"source": "intake/acq-example/source/material.md", "type": "text_file", "sha256": hashlib.sha256(self.original.read_bytes()).hexdigest(), "bytes": self.original.stat().st_size}],
            "dependencies": [],
            "missing_references": [],
            "unknowns": [],
            "limits": ["Analisi statica"],
            "analysis": {"method": "bounded_static_text_v1", "files_examined": 1}
        }
        (self.root / "proposals/class.example.json").write_text(
            json.dumps(self.proposal), encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def _material(self):
        catalog = json.loads((self.root / "catalog/materials.json").read_text(encoding="utf-8"))
        return catalog["materials"][0]

    def test_approval_updates_only_material_classification_and_records_decision(self):
        skills_before = (self.root / "catalog/skills.json").read_bytes()
        original_before = self.original.read_bytes()
        result = approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Esaminata e approvata.")
        classification = self._material()["classification"]
        self.assertEqual(classification["status"], "classified")
        self.assertEqual(classification["kind"], "skill")
        self.assertEqual(classification["confidence"], "medium")
        self.assertEqual(classification["decisions"][0]["decision"], "approved")
        self.assertEqual(result["decision"], "approved")
        expected_proposal_digest = hashlib.sha256(
            (self.root / "proposals/class.example.json").read_bytes()
        ).hexdigest()
        self.assertEqual(result["proposal_sha256"], expected_proposal_digest)
        self.assertEqual(classification["decisions"][0]["proposal_sha256"], expected_proposal_digest)
        self.assertEqual((self.root / "catalog/skills.json").read_bytes(), skills_before)
        self.assertEqual(self.original.read_bytes(), original_before)

    def test_rejection_records_decision_without_adding_a_skill(self):
        reject_proposal(self.root, "class.example", actor="human:reviewer", rationale="Gli indizi non bastano.")
        classification = self._material()["classification"]
        self.assertEqual(classification["status"], "unclassified")
        self.assertEqual(classification["kind"], "unclassified")
        self.assertEqual(classification["decisions"][0]["decision"], "rejected")
        self.assertEqual(json.loads((self.root / "catalog/skills.json").read_text())["skills"], [])

    def test_refuses_decision_when_original_fingerprint_changed(self):
        self.original.write_text("changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")
        self.assertEqual(self._material()["classification"]["status"], "not_examined")

    def test_preserves_error_when_proposal_fingerprint_is_stale(self):
        self.proposal["material"]["sha256"] = "0" * 64
        self.proposal["evidence"][0]["sha256"] = "0" * 64
        (self.root / "proposals/class.example.json").write_text(
            json.dumps(self.proposal), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "Il materiale è cambiato dopo l'analisi"):
            approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")

    def test_preserves_error_when_catalog_fingerprint_differs_from_proposal(self):
        path = self.root / "catalog/materials.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalog["materials"][0]["acquisition"]["original"]["sha256"] = "0" * 64
        path.write_text(json.dumps(catalog), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "La proposta non corrisponde all'impronta registrata"):
            approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")

    def test_refuses_decision_when_acquisition_is_no_longer_preserved(self):
        path = self.root / "catalog/materials.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalog["materials"][0]["acquisition"]["status"] = "incomplete"
        path.write_text(json.dumps(catalog), encoding="utf-8")
        with self.assertRaises(ValueError):
            approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")

    def test_refuses_second_decision_for_same_proposal(self):
        approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")
        with self.assertRaises(ValueError):
            reject_proposal(self.root, "class.example", actor="human:reviewer", rationale="Cambio idea")

    def test_requires_actor_and_reason(self):
        with self.assertRaises(ValueError):
            approve_proposal(self.root, "class.example", actor="", rationale="Ok")
        with self.assertRaises(ValueError):
            reject_proposal(self.root, "class.example", actor="human:reviewer", rationale=" ")

    def test_unknown_proposal_is_rejected(self):
        with self.assertRaises(FileNotFoundError):
            approve_proposal(self.root, "class.missing", actor="human:reviewer", rationale="Ok")

    def test_rejection_does_not_erase_a_previously_approved_classification(self):
        path = self.root / "catalog/materials.json"
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalog["materials"][0]["classification"] = {
            "status": "classified", "kind": "resource", "rationale": "Decisione precedente."
        }
        path.write_text(json.dumps(catalog), encoding="utf-8")
        reject_proposal(self.root, "class.example", actor="human:reviewer", rationale="Nuova proposta respinta.")
        classification = self._material()["classification"]
        self.assertEqual(classification["status"], "classified")
        self.assertEqual(classification["kind"], "resource")
        self.assertEqual(classification["decisions"][0]["decision"], "rejected")

    def test_rejects_proposal_with_invalid_evidence_hash(self):
        path = self.root / "proposals/class.example.json"
        self.proposal["evidence"][1]["sha256"] = "0" * 64
        path.write_text(json.dumps(self.proposal), encoding="utf-8")
        before = (self.root / "catalog/materials.json").read_bytes()
        with self.assertRaises(ValueError):
            approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")
        self.assertEqual((self.root / "catalog/materials.json").read_bytes(), before)

    def test_rejects_proposal_changed_between_review_and_commit(self):
        from scripts import classification_approval as approval
        original_catalog_reader = approval._read_catalog

        def change_after_catalog_snapshot(root):
            result = original_catalog_reader(root)
            path = self.root / "proposals/class.example.json"
            path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
            return result

        with patch("scripts.classification_approval._read_catalog", side_effect=change_after_catalog_snapshot):
            with self.assertRaisesRegex(ValueError, "proposta è cambiata"):
                approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")
        self.assertEqual(self._material()["classification"]["status"], "not_examined")

    def test_refuses_to_write_while_acquisition_catalog_lock_is_held(self):
        lock = self.root / ".materials-acquisition.lock"
        lock.write_text(json.dumps({
            "pid": os.getpid(), "hostname": socket.gethostname(),
            "created_at": "2026-11-03T00:00:00Z"
        }), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "già in corso"):
            approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")
        self.assertEqual(self._material()["classification"]["status"], "not_examined")

    def test_malformed_proposal_is_rejected_without_catalog_changes(self):
        path = self.root / "proposals/class.example.json"
        path.write_text(json.dumps({"proposal_id": "class.example", "status": "pending_approval", "material": []}), encoding="utf-8")
        before = (self.root / "catalog/materials.json").read_bytes()
        with self.assertRaises(ValueError):
            approve_proposal(self.root, "class.example", actor="human:reviewer", rationale="Ok")
        self.assertEqual((self.root / "catalog/materials.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
