import json
import tempfile
import unittest
from pathlib import Path

from scripts.gguf_four_config_diagnostic import consume_sse


class StreamingDiagnosticTests(unittest.TestCase):
    def test_preserves_each_content_delta_before_stream_finishes(self):
        events = [
            'data: ' + json.dumps({"choices":[{"delta":{"content":"{\\"kind\\""}}]}),
            'data: ' + json.dumps({"choices":[{"delta":{"content":":\\"skill\\"}"}}]}),
            'data: [DONE]',
        ]
        saved = []
        result = consume_sse(events, saved.append)
        self.assertEqual(result, '{"kind":"skill"}')
        self.assertEqual(saved, ['{"kind"', ':"skill"}'])

    def test_ignores_role_and_empty_delta_events(self):
        events = [
            'data: ' + json.dumps({"choices":[{"delta":{"role":"assistant"}}]}),
            'data: ' + json.dumps({"choices":[{"delta":{}}]}),
            'data: ' + json.dumps({"choices":[{"delta":{"content":"ok"}}]}),
            'data: [DONE]',
        ]
        saved = []
        self.assertEqual(consume_sse(events, saved.append), "ok")
        self.assertEqual(saved, ["ok"])


if __name__ == "__main__":
    unittest.main()
