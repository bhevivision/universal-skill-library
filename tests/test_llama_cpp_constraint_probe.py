import unittest

from scripts.llama_cpp_constraint_probe import is_constraint_response


class ConstrainedDecodingProbeTests(unittest.TestCase):
    def test_accepts_only_the_value_allowed_by_the_schema(self):
        self.assertTrue(is_constraint_response('{"result":"CONSTRAINT_APPLIED"}'))

    def test_rejects_value_the_schema_forbids(self):
        self.assertFalse(is_constraint_response('{"result":"NOT_ALLOWED"}'))

    def test_rejects_extra_properties(self):
        self.assertFalse(is_constraint_response('{"result":"CONSTRAINT_APPLIED","extra":true}'))

    def test_rejects_malformed_or_non_string_content(self):
        self.assertFalse(is_constraint_response('not json'))
        self.assertFalse(is_constraint_response(None))


if __name__ == "__main__":
    unittest.main()
