import tempfile
import unittest
from pathlib import Path

from scripts.semantic_extraction_evaluation import (
    match_expected_facts,
    run_extraction_evaluation,
    score_extraction,
)


class SemanticExtractionEvaluationTests(unittest.TestCase):
    def test_metrics_separate_fact_coverage_from_evidence_checks(self):
        rows = [
            {
                "expected_kind": "skill", "predicted_kind": "skill",
                "expected_facts": 4, "matched_facts": 3,
                "evidence_verified": True, "claims_total": 4,
                "claims_with_evidence": 4, "status": "completed", "error": None,
            },
            {
                "expected_kind": "tool", "predicted_kind": "skill",
                "expected_facts": 2, "matched_facts": 1,
                "evidence_verified": False, "claims_total": 2,
                "claims_with_evidence": 1, "status": "failed", "error": "invalid output",
            },
        ]

        metrics = score_extraction(rows)

        self.assertEqual(metrics["sample_count"], 2)
        self.assertEqual(metrics["kind_accuracy"], 0.5)
        self.assertEqual(metrics["expected_fact_coverage"], round(4 / 6, 4))
        self.assertEqual(metrics["evidence_verification_rate"], 0.5)
        self.assertEqual(metrics["claim_evidence_coverage"], round(5 / 6, 4))
        self.assertEqual(metrics["failed_samples"], 1)

    def test_expected_facts_are_matched_against_the_correct_semantic_fields(self):
        proposal = {
            "capabilities": [{
                "name": "Estrazione testo PDF",
                "description": "Estrae il testo dai documenti PDF.",
            }],
            "interfaces": {
                "inputs": [{"value": "File PDF"}],
                "outputs": [{"value": "File TXT in codifica UTF-8"}],
                "usage_conditions": [],
            },
            "dependencies": [{"name": "PyMuPDF"}],
            "tools_and_platforms": [{"name": "Python 3.11"}],
            "risks": [],
        }
        expected = {
            "capabilities": [["estrazione", "testo", "pdf"]],
            "inputs": [["file", "pdf"]],
            "outputs": [["file txt", "utf-8"]],
            "dependencies": [["pymupdf"]],
            "tools_and_platforms": [["python 3.11"]],
        }

        matched, total, details = match_expected_facts(expected, proposal)

        self.assertEqual((matched, total), (5, 5))
        self.assertTrue(all(item["matched"] for item in details))

    def test_full_pipeline_verifies_evidence_and_does_not_send_expected_labels(self):
        class FakeAdapter:
            analyzer_id = "test-full-extractor"
            version = "test-1"
            model = "fixture"
            model_version = "1"

            def analyze(self, request):
                self.assert_no_expected_data(request)
                item = request["selected_content"][0]
                return {
                    "schema_version": "1.0",
                    "proposal_id": "sem.placeholder",
                    "created_at": "2026-11-03T10:00:00Z",
                    "status": "completed",
                    "material": {
                        "id": request["material"]["id"],
                        "sha256": request["material"]["sha256"],
                        "original_kind": request["material"]["original_kind"],
                    },
                    "classification": {
                        "kind": "skill", "confidence": "high",
                        "rationale": "Descrive una procedura riutilizzabile.",
                        "summary": "Estrae testo da PDF.",
                        "evidence_refs": ["ev.source"], "evidence_quotes": [{"evidence_ref": "ev.source", "quote": "Accetta un file PDF e usa PyMuPDF per estrarre testo. Restituisce un file TXT UTF-8."}],
                    },
                    "capabilities": [{
                        "id": "cap.pdf-text", "name": "Estrazione testo PDF",
                        "description": "Estrae il testo dai documenti PDF.",
                        "certainty": "declared", "evidence_refs": ["ev.source"], "evidence_quotes": [{"evidence_ref": "ev.source", "quote": "Accetta un file PDF e usa PyMuPDF per estrarre testo. Restituisce un file TXT UTF-8."}],
                    }],
                    "interfaces": {
                        "inputs": [{"value": "File PDF", "certainty": "declared", "evidence_refs": ["ev.source"], "evidence_quotes": [{"evidence_ref": "ev.source", "quote": "Accetta un file PDF e usa PyMuPDF per estrarre testo. Restituisce un file TXT UTF-8."}]}],
                        "outputs": [{"value": "File TXT in codifica UTF-8", "certainty": "declared", "evidence_refs": ["ev.source"], "evidence_quotes": [{"evidence_ref": "ev.source", "quote": "Accetta un file PDF e usa PyMuPDF per estrarre testo. Restituisce un file TXT UTF-8."}]}],
                        "usage_conditions": [],
                    },
                    "dependencies": [{
                        "name": "PyMuPDF", "relationship": "installation",
                        "certainty": "declared", "evidence_refs": ["ev.source"], "evidence_quotes": [{"evidence_ref": "ev.source", "quote": "Accetta un file PDF e usa PyMuPDF per estrarre testo. Restituisce un file TXT UTF-8."}],
                    }],
                    "tools_and_platforms": [{
                        "name": "Python 3.11", "kind": "platform",
                        "compatibility": "mentioned_not_verified", "evidence_refs": ["ev.source"], "evidence_quotes": [{"evidence_ref": "ev.source", "quote": "Accetta un file PDF e usa PyMuPDF per estrarre testo. Restituisce un file TXT UTF-8."}],
                    }],
                    "evidence": [{
                        "id": "ev.source", "source": item["path"],
                        "sha256": item["sha256"], "kind": "text_file",
                    }],
                    "missing_references": [], "contradictions": [], "risks": [],
                    "unknowns": [], "limits": [],
                }

            @staticmethod
            def assert_no_expected_data(request):
                text = str(request).lower()
                if "expected_kind" in text or "expected_facts" in text:
                    raise AssertionError("Le etichette attese non devono raggiungere il modello.")

        dataset = {
            "dataset_version": "test",
            "samples": [{
                "id": "pdf-text",
                "expected_kind": "skill",
                "text": "# Estrazione PDF\nAccetta un file PDF e usa PyMuPDF per estrarre testo. Restituisce un file TXT UTF-8.",
                "expected_facts": {
                    "capabilities": [["estrazione", "testo", "pdf"]],
                    "inputs": [["file", "pdf"]],
                    "outputs": [["file txt", "utf-8"]],
                    "dependencies": [["pymupdf"]],
                    "tools_and_platforms": [["python 3.11"]],
                },
            }],
        }

        with tempfile.TemporaryDirectory() as work:
            report = run_extraction_evaluation(FakeAdapter(), dataset, work_root=Path(work))

        row = report["predictions"][0]
        self.assertEqual(row["status"], "completed")
        self.assertTrue(row["evidence_verified"])
        self.assertEqual(row["matched_facts"], row["expected_facts"])
        self.assertEqual(report["metrics"]["expected_fact_coverage"], 1.0)


if __name__ == "__main__":
    unittest.main()
