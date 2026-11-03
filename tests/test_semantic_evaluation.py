import unittest
from scripts.semantic_evaluation import build_request, score_predictions


class SemanticEvaluationTests(unittest.TestCase):
    def test_metrics_calculate_accuracy_macro_f1_and_evidence_fidelity(self):
        rows = [
            {"expected": "skill", "predicted": "skill", "evidence_valid": True},
            {"expected": "skill", "predicted": "tool", "evidence_valid": True},
            {"expected": "tool", "predicted": "tool", "evidence_valid": False},
            {"expected": "tool", "predicted": "tool", "evidence_valid": True},
        ]
        metrics = score_predictions(rows)
        self.assertEqual(metrics["sample_count"], 4)
        self.assertEqual(metrics["exact_accuracy"], 0.75)
        self.assertEqual(metrics["evidence_fidelity"], 0.75)
        self.assertEqual(metrics["per_class"]["skill"]["recall"], 0.5)
        self.assertAlmostEqual(metrics["per_class"]["tool"]["precision"], 2 / 3, places=3)

    def test_expected_label_is_not_sent_to_model(self):
        request = build_request({"id": "skill-01", "expected_kind": "skill", "text": "A skill description."})
        self.assertNotIn("expected_kind", request)
        self.assertNotIn("skill-01", request["selected_content"][0]["text"])
        self.assertFalse(request["safety"]["allow_process_execution"])


if __name__ == "__main__":
    unittest.main()
