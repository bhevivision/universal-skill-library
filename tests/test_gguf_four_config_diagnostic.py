import json
import unittest

from scripts.gguf_four_config_diagnostic import CONFIGURATIONS, _apply_configuration, consume_sse
from scripts.llama_cpp_adapter import _semantic_output_schema


class StreamingDiagnosticTests(unittest.TestCase):
    def test_preserves_each_content_delta_before_stream_finishes(self):
        events = [
            "data: " + json.dumps({"choices": [{"delta": {"content": '{"kind"'}}]}),
            "data: " + json.dumps({"choices": [{"delta": {"content": ':"skill"}'}}]}),
            "data: [DONE]",
        ]
        saved = []
        result = consume_sse(events, saved.append)
        self.assertEqual(result, '{"kind":"skill"}')
        self.assertEqual(saved, ['{"kind"', ':"skill"}'])

    def test_ignores_role_and_empty_delta_events(self):
        events = [
            "data: " + json.dumps({"choices": [{"delta": {"role": "assistant"}}]}),
            "data: " + json.dumps({"choices": [{"delta": {}}]}),
            "data: " + json.dumps({"choices": [{"delta": {"content": "ok"}}]}),
            "data: [DONE]",
        ]
        saved = []
        self.assertEqual(consume_sse(events, saved.append), "ok")
        self.assertEqual(saved, ["ok"])

    def test_captures_usage_event_without_content_choices(self):
        events = [
            "data: " + json.dumps({"choices": [{"delta": {"content": "{}"}}]}),
            "data: " + json.dumps({"choices": [], "usage": {"completion_tokens": 17}}),
            "data: [DONE]",
        ]
        seen = []
        consume_sse(events, lambda _chunk: None, seen.append)
        self.assertEqual(seen[1]["usage"]["completion_tokens"], 17)

    def test_four_configurations_isolate_pattern_and_array_changes(self):
        def collect(value, key, found):
            if isinstance(value, dict):
                if key in value:
                    found.append(value[key])
                for child in value.values():
                    collect(child, key, found)
            elif isinstance(value, list):
                for child in value:
                    collect(child, key, found)

        base = _semantic_output_schema()
        variants = {item["id"]: _apply_configuration(base, item) for item in CONFIGURATIONS}
        patterns = {}
        for key in variants:
            found = []
            collect(variants[key], "pattern", found)
            patterns[key] = found

        original = r"^(intake/|catalog/materials\.json$)"
        corrected = r"^(intake/.*|catalog/materials\.json)$"
        self.assertIn(original, patterns["A"])
        self.assertIn(original, patterns["B"])
        self.assertIn(corrected, patterns["C"])
        self.assertIn(corrected, patterns["D"])

        for key in ("B", "D"):
            def check_arrays(value):
                if isinstance(value, dict):
                    if value.get("type") == "array":
                        self.assertIn("maxItems", value)
                    for child in value.values():
                        check_arrays(child)
                elif isinstance(value, list):
                    for child in value:
                        check_arrays(child)
            check_arrays(variants[key])


if __name__ == "__main__":
    unittest.main()
