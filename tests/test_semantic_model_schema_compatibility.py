import unittest

from scripts.llama_cpp_adapter import _semantic_output_schema


class SemanticModelSchemaCompatibilityTests(unittest.TestCase):
    def test_schema_sent_to_llama_cpp_does_not_use_reference_expansion(self):
        schema = _semantic_output_schema()
        forbidden = []

        def visit(value, path="$"):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"$ref", "$defs"}:
                        forbidden.append(f"{path}/{key}")
                    visit(child, f"{path}/{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, f"{path}/{index}")

        visit(schema)

        self.assertEqual(
            forbidden,
            [],
            "Lo schema per llama.cpp deve essere autonomo: i riferimenti annidati "
            "possono causare espansione eccessiva della grammatica e generazione "
            "non vincolata.",
        )

    def test_schema_keeps_the_complete_semantic_contract(self):
        schema = _semantic_output_schema()

        self.assertEqual(schema["type"], "object")
        self.assertEqual(
            set(schema["required"]),
            {
                "status", "classification", "capabilities", "interfaces",
                "dependencies", "tools_and_platforms", "evidence",
                "missing_references", "contradictions", "risks", "unknowns", "limits",
            },
        )
        self.assertIn("classification", schema["properties"])
        self.assertIn("capabilities", schema["properties"])


if __name__ == "__main__":
    unittest.main()
