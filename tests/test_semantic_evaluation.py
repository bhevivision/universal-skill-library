import unittest
from scripts.semantic_evaluation import build_request, run_evaluation, score_predictions


class SemanticEvaluationTests(unittest.TestCase):
    def test_metrics_name_source_reference_integrity_without_claiming_semantic_fidelity(self):
        rows = [
            {"expected": "skill", "predicted": "skill", "evidence_valid": True},
            {"expected": "skill", "predicted": "tool", "evidence_valid": True},
            {"expected": "tool", "predicted": "tool", "evidence_valid": False},
            {"expected": "tool", "predicted": "tool", "evidence_valid": True},
        ]
        metrics = score_predictions(rows)
        self.assertEqual(metrics["sample_count"], 4)
        self.assertEqual(metrics["exact_accuracy"], 0.75)
        self.assertEqual(metrics["evidence_reference_integrity"], 0.75)
        self.assertNotIn("evidence_fidelity", metrics)
        self.assertEqual(metrics["per_class"]["skill"]["recall"], 0.5)
        self.assertAlmostEqual(metrics["per_class"]["tool"]["precision"], 2 / 3, places=3)

    def test_report_keeps_model_decision_diagnostics(self):
        class FakeAdapter:
            def analyze(self, request):
                return {
                    "status": "completed",
                    "classification": {
                        "kind": "skill",
                        "confidence": "medium",
                        "rationale": "Contiene istruzioni operative riutilizzabili.",
                        "summary": "Una skill.",
                        "evidence_refs": ["ev.sample"],
                    },
                    "evidence": [{
                        "id": "ev.sample",
                        "source": request["files"][0]["path"],
                        "sha256": request["files"][0]["sha256"],
                        "kind": "text_file",
                    }],
                }

        dataset = {
            "dataset_version": "test",
            "samples": [{
                "id": "skill-01",
                "expected_kind": "skill",
                "text": "Procedura riutilizzabile.",
            }],
        }
        report = run_evaluation(FakeAdapter(), dataset)
        row = report["predictions"][0]
        self.assertEqual(row["predicted"], "skill")
        self.assertEqual(row["model_status"], "completed")
        self.assertEqual(row["classification"]["confidence"], "medium")
        self.assertEqual(row["classification"]["rationale"], "Contiene istruzioni operative riutilizzabili.")
        self.assertTrue(row["evidence_valid"])

    def test_expected_label_is_not_sent_to_model(self):
        request = build_request({"id": "skill-01", "expected_kind": "skill", "text": "A skill description."})
        self.assertNotIn("expected_kind", request)
        self.assertNotIn("skill-01", request["selected_content"][0]["text"])
        self.assertFalse(request["safety"]["allow_process_execution"])


if __name__ == "__main__":
    unittest.main()
