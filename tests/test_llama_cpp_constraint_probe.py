import unittest

from scripts.llama_cpp_constraint_probe import build_payload, is_constraint_response


class ConstrainedDecodingProbeTests(unittest.TestCase):
    def test_accepts_only_the_value_allowed_by_the_constraint(self):
        self.assertTrue(is_constraint_response('{"result":"CONSTRAINT_APPLIED"}'))

    def test_rejects_value_the_constraint_forbids(self):
        self.assertFalse(is_constraint_response('{"result":"NOT_ALLOWED"}'))

    def test_rejects_extra_properties(self):
        self.assertFalse(is_constraint_response('{"result":"CONSTRAINT_APPLIED","extra":true}'))

    def test_rejects_malformed_or_non_string_content(self):
        self.assertFalse(is_constraint_response("not json"))
        self.assertFalse(is_constraint_response(None))

    def test_documented_top_level_schema_form_is_recorded_as_legacy_control(self):
        payload = build_payload("response_format_documented")
        self.assertEqual(payload["response_format"]["schema"]["properties"]["result"]["enum"], ["CONSTRAINT_APPLIED"])
        self.assertNotIn("grammar", payload)

    def test_nested_json_schema_wrapper_is_used_for_compatible_request(self):
        payload = build_payload("response_format_nested")
        self.assertEqual(
            payload["response_format"]["json_schema"]["schema"]["properties"]["result"]["enum"],
            ["CONSTRAINT_APPLIED"],
        )
        self.assertNotIn("schema", payload["response_format"])

    def test_explicit_grammar_bypasses_json_schema_conversion(self):
        payload = build_payload("grammar")
        self.assertIn("root ::=", payload["grammar"])
        self.assertNotIn("response_format", payload)


if __name__ == "__main__":
    unittest.main()
