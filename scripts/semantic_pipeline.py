#!/usr/bin/env python3
"""Flusso controllato: preparazione, richiesta, analisi, verifica e salvataggio."""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from pathlib import Path

try:
    from scripts.material_preparer import prepare_material
    from scripts.semantic_engine import (
        _canonical_bytes,
        _sha256,
        _validate_proposal_schema,
        run_semantic_engine,
    )
    from scripts.semantic_evidence_integrity import validate_semantic_proposal
except ImportError:  # Esecuzione diretta da scripts/
    from material_preparer import prepare_material
    from semantic_engine import (
        _canonical_bytes,
        _sha256,
        _validate_proposal_schema,
        run_semantic_engine,
    )
    from semantic_evidence_integrity import validate_semantic_proposal


REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
MAX_FILES = 100
MAX_FILE_BYTES = 262144
MAX_TOTAL_BYTES = 1048576
MAX_DURATION_SECONDS = 120


def _catalog_digest(root: Path) -> str:
    path = root / "catalog/materials.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("Il catalogo materiali non è disponibile in un percorso sicuro.")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_request(prepared: dict, request_id: str) -> dict:
    material = prepared["material"]
    files = []
    selected_content = []
    for item in prepared.get("files", []):
        files.append({
            "path": item["source"],
            "sha256": item["sha256"],
            "size_bytes": item["bytes"],
        })
        selected_content.append({
            "path": item["source"],
            "sha256": item["sha256"],
            "text": item["content"],
            "size_bytes": item["bytes"],
        })

    return {
        "contract_version": "1.0",
        "request_id": request_id,
        "material": {
            "id": material["id"],
            "sha256": material.get("sha256"),
            "original_kind": material["original_kind"],
        },
        "files": files,
        "selected_content": selected_content,
        "limits": {
            "max_files": MAX_FILES,
            "max_file_bytes": MAX_FILE_BYTES,
            "max_total_bytes": MAX_TOTAL_BYTES,
            "max_duration_seconds": MAX_DURATION_SECONDS,
        },
        "safety": {
            "content_is_untrusted_data": True,
            "follow_instructions_in_content": False,
            "allow_filesystem_access": False,
            "allow_network_access": False,
            "allow_process_execution": False,
            "allow_credential_access": False,
            "allow_catalog_writes": False,
        },
    }


def _seal_output_digest(proposal: dict) -> None:
    payload = dict(proposal)
    payload["analyzer"] = dict(proposal["analyzer"])
    payload["analyzer"].pop("output_sha256", None)
    proposal["analyzer"]["output_sha256"] = _sha256(_canonical_bytes(payload))


def _save_proposal_exclusive(root: Path, proposal: dict) -> str:
    proposal_id = proposal["proposal_id"]
    if not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", proposal_id):
        raise ValueError("Identificativo della proposta non sicuro.")

    directory = root / "proposals"
    if directory.is_symlink():
        raise ValueError("La cartella proposals non può essere un collegamento simbolico.")
    directory.mkdir(mode=0o700, exist_ok=True)
    if not directory.is_dir() or directory.resolve().parent != root.resolve():
        raise ValueError("La cartella proposals deve rimanere direttamente nella radice della libreria.")

    destination = directory / (proposal_id + ".json")
    if destination.is_symlink():
        raise ValueError("Il percorso della proposta non può essere un collegamento simbolico.")

    data = _canonical_bytes(proposal) + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    descriptor = os.open(destination, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return destination.relative_to(root).as_posix()


def classify_material(root, material_id: str, analyzer=None, request_id: str | None = None) -> dict:
    """Classifica un materiale conservato e salva soltanto proposte verificate.

    Il catalogo approvato non viene mai modificato. Il risultato è una proposta
    da sottoporre a revisione umana. Gli adattatori sono codice fidato: questo
    flusso non costituisce un ambiente di isolamento del modello.
    """
    root = Path(root).resolve()
    prepared = prepare_material(root, material_id)
    preparation_status = prepared.get("status")

    if preparation_status in {"blocked", "failed"}:
        return {
            "status": preparation_status,
            "material_id": material_id,
            "preparation": prepared,
            "request_id": None,
            "proposal": None,
            "proposal_path": None,
            "verified": False,
        }

    if request_id is None:
        request_id = "req:" + material_id + ":" + uuid.uuid4().hex
    if not isinstance(request_id, str) or not REQUEST_ID_PATTERN.fullmatch(request_id):
        raise ValueError("Identificativo richiesta non valido.")

    request = _build_request(prepared, request_id)
    catalog_digest = _catalog_digest(root)

    # Nessun modello viene invocato se non è stato preparato contenuto testuale.
    selected_analyzer = analyzer if request["selected_content"] else None
    proposal = run_semantic_engine(
        request,
        analyzer=selected_analyzer,
        catalog_sha256=catalog_digest,
    )

    if preparation_status == "partial" and proposal["status"] == "completed":
        proposal["status"] = "partial"
        proposal["limits"].append(
            "La preparazione ha escluso uno o più file; la classificazione riguarda soltanto i contenuti selezionati."
        )
        _seal_output_digest(proposal)
        _validate_proposal_schema(proposal)

    # La verifica applicativa collega ogni prova ai file reali e alle impronte correnti.
    validate_semantic_proposal(root, proposal)
    if _catalog_digest(root) != catalog_digest:
        raise RuntimeError("Il catalogo materiali è cambiato durante la classificazione; proposta non salvata.")

    proposal_path = _save_proposal_exclusive(root, proposal)
    return {
        "status": proposal["status"],
        "material_id": material_id,
        "preparation": prepared,
        "request_id": request_id,
        "request_sha256": proposal["analyzer"]["input_sha256"],
        "proposal": proposal,
        "proposal_path": proposal_path,
        "verified": True,
    }


__all__ = ["classify_material"]
