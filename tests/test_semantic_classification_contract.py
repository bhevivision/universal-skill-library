import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/semantic-classification-proposal.schema.json"


def valid_proposal():
    return {
        "schema_version": "1.0",
        "proposal_id": "sem.example",
        "created_at": "2026-11-02T10:00:00Z",
        "status": "completed",
        "material": {
            "id": "acq.example",
            "sha256": "a" * 64,
            "original_kind": "directory"
        },
        "classification": {
            "kind": "skill",
            "confidence": "medium",
            "rationale": "Il materiale descrive istruzioni operative riutilizzabili.",
            "summary": "Assiste nella produzione di relazioni.",
            "evidence_refs": ["ev.instructions"]
        },
        "capabilities": [{
            "id": "cap.report",
            "name": "Produzione di relazioni",
            "description": "Organizza fonti e produce una relazione strutturata.",
            "certainty": "declared",
            "evidence_refs": ["ev.instructions"]
        }],
        "interfaces": {
            "inputs": [{
                "value": "Documenti sorgente",
                "certainty": "declared",
                "evidence_refs": ["ev.instructions"]
            }],
            "outputs": [{
                "value": "Relazione strutturata",
                "certainty": "declared",
                "evidence_refs": ["ev.instructions"]
            }],
            "usage_conditions": [{
                "value": "Richiede documenti sorgente leggibili",
                "certainty": "inferred",
                "evidence_refs": ["ev.instructions"]
            }]
        },
        "dependencies": [{
            "name": "Python",
            "relationship": "runtime",
            "certainty": "declared",
            "evidence_refs": ["ev.requirements"]
        }],
        "tools_and_platforms": [{
            "name": "Codex",
            "kind": "platform",
            "compatibility": "mentioned_not_verified",
            "evidence_refs": ["ev.instructions"]
        }],
        "evidence": [{
            "id": "ev.instructions",
            "source": "intake/acq-example/source/SKILL.md",
            "sha256": "b" * 64,
            "kind": "text_file",
            "location": {"start_line": 12, "end_line": 18}
        }, {
            "id": "ev.requirements",
            "source": "intake/acq-example/source/requirements.txt",
            "sha256": "c" * 64,
            "kind": "text_file"
        }],
        "missing_references": [],
        "contradictions": [],
        "risks": [],
        "unknowns": ["La compatibilità effettiva non è stata verificata."],
        "limits": ["Nessun codice è stato eseguito."],
        "analyzer": {
            "id": "local-semantic-analyzer",
            "version": "0.1.0",
            "provider": "local",
            "model": "example-model",
            "model_version": "2026-10",
            "input_sha256": "d" * 64,
            "output_sha256": "e" * 64
        }
    }


class SemanticClassificationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def assert_invalid(self, proposal, field):
        errors = list(self.validator.iter_errors(proposal))
        self.assertTrue(errors, f"La proposta doveva essere rifiutata: {field}")
        self.assertTrue(
            any(field in ".".join(str(part) for part in error.absolute_path) or field in error.message for error in errors),
            f"Nessun errore relativo a {field}: {[error.message for error in errors]}"
        )

    def test_accepts_complete_proposal_with_evidence(self):
        self.assertEqual(list(self.validator.iter_errors(valid_proposal())), [])

    def test_rejects_unknown_top_level_fields(self):
        proposal = valid_proposal()
        proposal["source_excerpt"] = "testo copiato dal materiale"
        self.assert_invalid(proposal, "source_excerpt")

    def test_rejects_unknown_classification_category(self):
        proposal = valid_proposal()
        proposal["classification"]["kind"] = "magic"
        self.assert_invalid(proposal, "kind")

    def test_rejects_invalid_analysis_status(self):
        proposal = valid_proposal()
        proposal["status"] = "approved"
        self.assert_invalid(proposal, "status")

    def test_rejects_capability_without_evidence(self):
        proposal = valid_proposal()
        proposal["capabilities"][0]["evidence_refs"] = []
        self.assert_invalid(proposal, "evidence_refs")

    def test_rejects_declared_claim_without_evidence(self):
        proposal = valid_proposal()
        proposal["interfaces"]["inputs"][0]["evidence_refs"] = []
        self.assert_invalid(proposal, "evidence_refs")

    def test_allows_unknown_claim_without_evidence(self):
        proposal = valid_proposal()
        proposal["interfaces"]["usage_conditions"][0] = {
            "value": "Condizione non determinabile",
            "certainty": "unknown",
            "evidence_refs": []
        }
        self.assertEqual(list(self.validator.iter_errors(proposal)), [])

    def test_rejects_evidence_with_invalid_fingerprint(self):
        proposal = valid_proposal()
        proposal["evidence"][0]["sha256"] = "not-a-sha256"
        self.assert_invalid(proposal, "sha256")

    def test_rejects_compatibility_claimed_as_verified(self):
        proposal = valid_proposal()
        proposal["tools_and_platforms"][0]["compatibility"] = "verified"
        self.assert_invalid(proposal, "compatibility")

    def test_rejects_duplicate_evidence_identifiers(self):
        proposal = valid_proposal()
        proposal["evidence"].append(dict(proposal["evidence"][0]))
        self.assert_invalid(proposal, "evidence")


    def test_rejects_remote_analyzer_without_explicit_external_authorization(self):
        proposal = valid_proposal()
        proposal["analyzer"]["provider"] = "remote"
        proposal["analyzer"]["external_data_authorized"] = False
        self.assert_invalid(proposal, "external_data_authorized")

    def test_rejects_local_analyzer_marked_as_external(self):
        proposal = valid_proposal()
        proposal["analyzer"]["external_data_authorized"] = True
        self.assert_invalid(proposal, "external_data_authorized")

    def test_rejects_evidence_outside_preserved_material(self):
        proposal = valid_proposal()
        proposal["evidence"][0]["source"] = "downloads/copied.md"
        self.assert_invalid(proposal, "source")

    def test_rejects_missing_required_contract_field(self):
        proposal = valid_proposal()
        del proposal["analyzer"]["input_sha256"]
        self.assert_invalid(proposal, "input_sha256")


    def test_rejects_classification_without_supporting_evidence(self):
        proposal = valid_proposal()
        proposal["classification"]["evidence_refs"] = []
        self.assert_invalid(proposal, "evidence_refs")


if __name__ == "__main__":
    unittest.main()
