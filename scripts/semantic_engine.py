#!/usr/bin/env python3
"""Motore semantico sostituibile: valida l'ingresso e non simula analisi assenti."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

try:
    from scripts.semantic_evidence_integrity import validate_semantic_request
except ImportError:  # Esecuzione diretta da scripts/
    from semantic_evidence_integrity import validate_semantic_request


PROPOSAL_SCHEMA = (
    Path(__file__).resolve().parents[1]
    / "schemas"
    / "semantic-classification-proposal.schema.json"
)


def _canonical_bytes(value: dict) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _proposal_id(request_id: str) -> str:
    normalized = re.sub(r"[^a-z0-9.-]+", "-", request_id.lower()).strip(".-")
    if not normalized or not normalized[0].isalnum():
        normalized = "request-" + normalized
    return "sem." + normalized[:110]


def _base_proposal(request: dict, catalog_sha256: str, status: str, reason: str) -> dict:
    request_digest = _sha256(_canonical_bytes(request))
    proposal = {
        "schema_version": "1.0",
        "proposal_id": _proposal_id(request["request_id"]),
        "created_at": _now(),
        "status": status,
        "material": {
            "id": request["material"]["id"],
            "sha256": request["material"]["sha256"],
            "original_kind": request["material"]["original_kind"],
        },
        "classification": {
            "kind": "unclassified",
            "confidence": "low",
            "rationale": reason,
            "summary": "Non è disponibile una classificazione semantica verificata.",
            "evidence_refs": ["ev.catalog"],
        },
        "capabilities": [],
        "interfaces": {"inputs": [], "outputs": [], "usage_conditions": []},
        "dependencies": [],
        "tools_and_platforms": [],
        "evidence": [{
            "id": "ev.catalog",
            "source": "catalog/materials.json",
            "sha256": catalog_sha256,
            "kind": "metadata",
        }],
        "missing_references": [],
        "contradictions": [],
        "risks": [],
        "unknowns": [reason],
        "limits": [
            "Nessuna affermazione sul contenuto è stata prodotta.",
            "La proposta non è approvata e non autorizza l'esecuzione del materiale.",
        ],
        "analyzer": {
            "id": "universal-semantic-engine",
            "version": "0.1.0",
            "provider": "local",
            "model": None,
            "model_version": None,
            "external_data_authorized": False,
            "input_sha256": request_digest,
            "output_sha256": "0" * 64,
        },
    }
    # L'impronta d'uscita copre la proposta escluso il campo che la contiene.
    digest_payload = dict(proposal)
    digest_payload["analyzer"] = dict(proposal["analyzer"])
    digest_payload["analyzer"].pop("output_sha256")
    proposal["analyzer"]["output_sha256"] = _sha256(_canonical_bytes(digest_payload))
    return proposal


def _validate_proposal_schema(proposal: dict) -> None:
    try:
        schema = json.loads(PROPOSAL_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Schema della proposta semantica non disponibile o non valido.") from exc
    errors = sorted(validator.iter_errors(proposal), key=lambda error: list(error.absolute_path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "proposta"
        raise ValueError(f"Proposta dell'analizzatore non conforme in {location}: {error.message}")


def run_semantic_engine(
    request: dict,
    analyzer=None,
    catalog_sha256: str | None = None,
) -> dict:
    """Esegue un adattatore locale oppure restituisce una proposta not_available.

    Un adattatore fidato espone analyze(request) e restituisce i campi semantici
    della proposta, esclusa la sezione analyzer. Il suo codice non viene isolato
    da questa funzione: l'isolamento reale richiede un ambiente separato.
    """
    validate_semantic_request(request)
    if not isinstance(catalog_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", catalog_sha256):
        raise ValueError("È richiesta l'impronta SHA-256 corrente di catalog/materials.json.")

    if analyzer is None:
        proposal = _base_proposal(
            request,
            catalog_sha256,
            "not_available",
            "Nessun analizzatore semantico locale è configurato o disponibile.",
        )
        _validate_proposal_schema(proposal)
        return proposal

    analyze = getattr(analyzer, "analyze", None)
    if not callable(analyze):
        raise ValueError("L'analizzatore deve esporre il metodo analyze(request).")

    try:
        result = analyze(request)
        if not isinstance(result, dict):
            raise ValueError("L'analizzatore non ha restituito un oggetto proposta.")
        proposal = dict(result)
        proposal["analyzer"] = {
            "id": str(getattr(analyzer, "analyzer_id", "local-adapter")),
            "version": str(getattr(analyzer, "version", "unknown")),
            "provider": "local",
            "model": getattr(analyzer, "model", None),
            "model_version": getattr(analyzer, "model_version", None),
            "external_data_authorized": False,
            "input_sha256": _sha256(_canonical_bytes(request)),
            "output_sha256": "0" * 64,
        }
        digest_payload = dict(proposal)
        digest_payload["analyzer"] = dict(proposal["analyzer"])
        digest_payload["analyzer"].pop("output_sha256")
        proposal["analyzer"]["output_sha256"] = _sha256(_canonical_bytes(digest_payload))
        _validate_proposal_schema(proposal)
        if proposal["material"] != {
            "id": request["material"]["id"],
            "sha256": request["material"]["sha256"],
            "original_kind": request["material"]["original_kind"],
        }:
            raise ValueError("L'analizzatore ha restituito un'identità del materiale diversa dalla richiesta.")
        return proposal
    except Exception as exc:
        # Non conservare un risultato parziale o potenzialmente malformato.
        proposal = _base_proposal(
            request,
            catalog_sha256,
            "failed",
            "L'analisi semantica non è stata completata: " + type(exc).__name__ + ".",
        )
        _validate_proposal_schema(proposal)
        return proposal


__all__ = ["run_semantic_engine"]
