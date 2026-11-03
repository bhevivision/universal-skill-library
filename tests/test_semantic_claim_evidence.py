import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.semantic_claim_evidence import normalize_model_json, validate_claim_evidence


class ModelResponseNormalizationTests(unittest.TestCase):
    def test_accepts_plain_json(self):
        self.assertEqual(normalize_model_json('{"status":"partial"}'), {"status": "partial"})

    def test_extracts_json_from_fenced_block_and_surrounding_text(self):
        raw = 'Risultato:\n```json\n{"status":"partial"}\n```\nFine.'
        self.assertEqual(normalize_model_json(raw), {"status": "partial"})

    def test_rejects_truncated_json(self):
        with self.assertRaises(ValueError):
            normalize_model_json('{"status":')

    def test_rejects_non_object_and_malformed_fields(self):
        with self.assertRaises(ValueError):
            normalize_model_json('[1, 2]')
        with self.assertRaises(ValueError):
            normalize_model_json('{"status":"completed","status":"partial"}')


class ExactClaimEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "intake" / "sample" / "source.md"
        self.source.parent.mkdir(parents=True)
        self.text = "Questa skill legge documenti PDF.\nProduce un rapporto verificabile.\n"
        self.source.write_text(self.text, encoding="utf-8")
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.proposal = {
            "status": "partial",
            "evidence": [{
                "id": "ev.source",
                "source": "intake/sample/source.md",
                "sha256": self.digest,
                "kind": "text_file"
            }],
            "classification": {
                "kind": "skill",
                "rationale": "Questa skill legge documenti PDF.",
                "summary": "Produce un rapporto verificabile.",
                "evidence_refs": ["ev.source"],
                "evidence_quotes": [
                    {"evidence_ref": "ev.source", "quote": "Questa skill legge documenti PDF."},
                    {"evidence_ref": "ev.source", "quote": "Produce un rapporto verificabile."}
                ]
            },
            "capabilities": [{
                "name": "Lettura PDF",
                "description": "Legge documenti PDF.",
                "evidence_refs": ["ev.source"],
                "evidence_quotes": [{"evidence_ref": "ev.source", "quote": "Questa skill legge documenti PDF."}]
            }],
            "interfaces": {"inputs": [], "outputs": [], "usage_conditions": []},
            "dependencies": [],
            "tools_and_platforms": []
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_exact_quotes_from_the_referenced_hashed_file(self):
        self.assertTrue(validate_claim_evidence(self.root, self.proposal))

    def test_rejects_claim_without_quotes(self):
        del self.proposal["classification"]["evidence_quotes"]
        with self.assertRaises(ValueError):
            validate_claim_evidence(self.root, self.proposal)

    def test_rejects_invented_quote(self):
        self.proposal["classification"]["evidence_quotes"][0]["quote"] = "Invented text."
        with self.assertRaises(ValueError):
            validate_claim_evidence(self.root, self.proposal)

    def test_rejects_quote_linked_to_different_evidence_reference(self):
        self.proposal["classification"]["evidence_quotes"][0]["evidence_ref"] = "ev.other"
        with self.assertRaises(ValueError):
            validate_claim_evidence(self.root, self.proposal)

    def test_rejects_claim_when_request_has_no_selected_sources(self):
        with self.assertRaisesRegex(ValueError, "file selezionato"):
            validate_claim_evidence(self.root, self.proposal, allowed_sources={})

    def test_rejects_conflicting_digest_for_cached_source_path(self):
        altered = dict(self.proposal["evidence"][0])
        altered["id"] = "ev.altered"
        altered["sha256"] = "0" * 64
        self.proposal["evidence"].append(altered)
        self.proposal["capabilities"][0]["evidence_refs"] = ["ev.altered"]
        self.proposal["capabilities"][0]["evidence_quotes"] = [
            {"evidence_ref": "ev.altered", "quote": "Questa skill legge documenti PDF."}
        ]
        with self.assertRaisesRegex(ValueError, "impronta SHA-256"):
            validate_claim_evidence(self.root, self.proposal)

    def test_rejects_source_fingerprint_mismatch(self):
        self.source.write_text("File modificato.\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            validate_claim_evidence(self.root, self.proposal)

    def test_rejects_completed_when_any_claim_is_unsupported(self):
        self.proposal["status"] = "completed"
        self.proposal["capabilities"][0]["evidence_quotes"] = []
        with self.assertRaises(ValueError):
            validate_claim_evidence(self.root, self.proposal)


if __name__ == "__main__":
    unittest.main()
