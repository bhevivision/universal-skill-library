import hashlib
import json
import unittest

from scripts.semantic_engine import run_semantic_engine


def valid_request():
    return {
        "contract_version": "1.0",
        "request_id": "req.engine-001",
        "material": {
            "id": "acq.example",
            "sha256": "a" * 64,
            "original_kind": "file"
        },
        "files": [{
            "path": "intake/acq-example/source/SKILL.md",
            "sha256": "b" * 64,
            "size_bytes": 24
        }],
        "selected_content": [{
            "path": "intake/acq-example/source/SKILL.md",
            "sha256": "b" * 64,
            "text": "Use supplied documents.",
            "size_bytes": 23
        }],
        "limits": {
            "max_files": 10,
            "max_file_bytes": 262144,
            "max_total_bytes": 1048576,
            "max_duration_seconds": 120
        },
        "safety": {
            "content_is_untrusted_data": True,
            "follow_instructions_in_content": False,
            "allow_filesystem_access": False,
            "allow_network_access": False,
            "allow_process_execution": False,
            "allow_credential_access": False,
            "allow_catalog_writes": False
        }
    }


class SemanticEngineTests(unittest.TestCase):
    def test_without_adapter_returns_explicit_not_available_proposal(self):
        request = valid_request()
        catalog_digest = "c" * 64

        proposal = run_semantic_engine(request, catalog_sha256=catalog_digest)

        self.assertEqual(proposal["status"], "not_available")
        self.assertEqual(proposal["classification"]["kind"], "unclassified")
        self.assertEqual(proposal["classification"]["confidence"], "low")
        self.assertEqual(proposal["capabilities"], [])
        self.assertEqual(proposal["evidence"][0]["source"], "catalog/materials.json")
        self.assertEqual(proposal["evidence"][0]["sha256"], catalog_digest)
        self.assertEqual(proposal["analyzer"]["provider"], "local")
        self.assertEqual(proposal["analyzer"]["external_data_authorized"], False)

    def test_request_fingerprint_is_deterministic(self):
        first = run_semantic_engine(valid_request(), catalog_sha256="c" * 64)
        second = run_semantic_engine(valid_request(), catalog_sha256="c" * 64)

        self.assertEqual(first["analyzer"]["input_sha256"], second["analyzer"]["input_sha256"])
        self.assertEqual(
            first["analyzer"]["input_sha256"],
            hashlib.sha256(json.dumps(valid_request(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
        )

    def test_invalid_request_is_rejected_before_adapter_invocation(self):
        class Adapter:
            called = False

            def analyze(self, request):
                self.called = True
                raise AssertionError("The adapter must not be invoked.")

        adapter = Adapter()
        request = valid_request()
        request["safety"]["allow_network_access"] = True

        with self.assertRaises(ValueError):
            run_semantic_engine(request, analyzer=adapter, catalog_sha256="c" * 64)

        self.assertFalse(adapter.called)

    def test_adapter_cannot_mutate_the_validated_request_or_its_fingerprint(self):
        request = valid_request()
        expected_digest = hashlib.sha256(
            json.dumps(request, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()

        class Adapter:
            def analyze(self, adapter_request):
                adapter_request["safety"]["allow_network_access"] = True
                raise RuntimeError("adapter stopped")

        proposal = run_semantic_engine(
            request, analyzer=Adapter(), catalog_sha256="c" * 64
        )

        self.assertEqual(proposal["status"], "failed")
        self.assertEqual(proposal["analyzer"]["input_sha256"], expected_digest)
        self.assertFalse(request["safety"]["allow_network_access"])


    def test_schema_failure_reports_safe_field_diagnostic(self):
        class InvalidAdapter:
            def analyze(self, request):
                item = request["selected_content"][0]
                return {
                    "status": "completed",
                    "classification": {
                        "kind": "invalid-kind",
                        "confidence": "high",
                        "rationale": "Motivazione.",
                        "summary": "Sintesi.",
                        "evidence_refs": ["ev.source"],
                    },
                    "capabilities": [],
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

        proposal = run_semantic_engine(
            valid_request(), analyzer=InvalidAdapter(), catalog_sha256="c" * 64
        )

        self.assertEqual(proposal["status"], "failed")
        self.assertIn("classification.kind", proposal["limits"][0])
        self.assertIn("enum", proposal["limits"][0])

    def test_missing_catalog_fingerprint_is_rejected(self):
        with self.assertRaises(ValueError):
            run_semantic_engine(valid_request())


if __name__ == "__main__":
    unittest.main()
