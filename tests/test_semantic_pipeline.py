import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.semantic_pipeline import classify_material


def build_library(root):
    source_dir = root / "intake/acq-example/source"
    source_dir.mkdir(parents=True)
    source = source_dir / "SKILL.md"
    source.write_text(
        "---\nname: example-skill\ndescription: A small example skill.\n---\n\n"
        "Use the supplied documents and return a concise summary.\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    record = {
        "id": "acq.example",
        "acquisition": {
            "status": "preserved",
            "acquired_at": "2026-11-02T10:00:00Z",
            "method": "copy",
            "original": {
                "kind": "file",
                "path": "intake/acq-example/source/SKILL.md",
                "sha256": digest,
                "digest_algorithm": "sha256-file-v1",
            },
        },
        "classification": {"status": "not_examined", "kind": "unclassified"},
        "documentation": {"status": "unknown"},
        "verification": {"status": "not_verified"},
        "usability": {"status": "not_assessed"},
    }
    catalog = root / "catalog/materials.json"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(
        json.dumps({"catalog_version": "1.0", "materials": [record]}, indent=2) + "\n",
        encoding="utf-8",
    )
    return source, digest


class SemanticPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.digest = build_library(self.root)

    def test_without_local_model_creates_only_unavailable_unclassified_proposal(self):
        result = classify_material(self.root, "acq.example")

        self.assertEqual(result["status"], "not_available")
        self.assertEqual(result["proposal"]["classification"]["kind"], "unclassified")
        self.assertEqual(result["proposal"]["capabilities"], [])
        self.assertTrue((self.root / result["proposal_path"]).is_file())
        self.assertEqual(len(list((self.root / "proposals").glob("*.json"))), 1)

    def test_local_adapter_result_is_evidence_checked_before_save(self):
        class Adapter:
            analyzer_id = "test-local-model"
            version = "test-1"
            model = "fixture-model"
            model_version = "1"

            def analyze(self, request):
                item = request["selected_content"][0]
                return {
                    "schema_version": "1.0",
                    "proposal_id": "sem.placeholder",
                    "created_at": "2026-11-02T10:00:00Z",
                    "status": "completed",
                    "material": {
                        "id": request["material"]["id"],
                        "sha256": request["material"]["sha256"],
                        "original_kind": request["material"]["original_kind"],
                    },
                    "classification": {
                        "kind": "skill",
                        "confidence": "medium",
                        "rationale": "Le istruzioni descrivono un comportamento riutilizzabile.",
                        "summary": "Istruzioni operative riutilizzabili.",
                        "evidence_refs": ["ev.source"],
                    },
                    "capabilities": [{
                        "id": "cap.document-summary",
                        "name": "Sintesi di documenti",
                        "description": "Produce una sintesi dei documenti forniti.",
                        "certainty": "declared",
                        "evidence_refs": ["ev.source"],
                    }],
                    "interfaces": {"inputs": [], "outputs": [], "usage_conditions": []},
                    "dependencies": [],
                    "tools_and_platforms": [],
                    "evidence": [{
                        "id": "ev.source",
                        "source": item["path"],
                        "sha256": item["sha256"],
                        "kind": "text_file",
                    }],
                    "missing_references": [],
                    "contradictions": [],
                    "risks": [],
                    "unknowns": [],
                    "limits": [],
                }

        result = classify_material(self.root, "acq.example", analyzer=Adapter())

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["proposal"]["classification"]["kind"], "skill")
        self.assertEqual(result["proposal"]["analyzer"]["id"], "test-local-model")
        self.assertTrue((self.root / result["proposal_path"]).is_file())

    def test_existing_proposal_is_never_overwritten(self):
        first = classify_material(self.root, "acq.example")
        saved = self.root / first["proposal_path"]
        original = saved.read_bytes()

        with self.assertRaises(FileExistsError):
            classify_material(self.root, "acq.example", request_id=first["request_id"])

        self.assertEqual(saved.read_bytes(), original)
        self.assertEqual(len(list((self.root / "proposals").glob("*.json"))), 1)

    def test_blocked_material_is_not_sent_to_adapter_or_saved(self):
        class Adapter:
            called = False

            def analyze(self, request):
                self.called = True
                raise AssertionError("Blocked material must not reach the model.")

        adapter = Adapter()
        self.source.write_text("tampered", encoding="utf-8")

        result = classify_material(self.root, "acq.example", analyzer=adapter)

        self.assertEqual(result["status"], "blocked")
        self.assertFalse(adapter.called)
        self.assertIsNone(result["proposal_path"])
        self.assertFalse((self.root / "proposals").exists())


if __name__ == "__main__":
    unittest.main()
