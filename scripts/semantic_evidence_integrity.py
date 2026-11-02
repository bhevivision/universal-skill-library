#!/usr/bin/env python3
"""Controlli applicativi di integrità delle prove nelle proposte semantiche."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker

from scripts.classify_material import _fingerprint, _load_catalog, _record_original_path


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/semantic-classification-proposal.schema.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("Percorso della prova non valido.")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("Percorso della prova non valido o contiene attraversamento di cartelle.")
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Collegamento simbolico non ammesso nel percorso della prova: {value}")
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"File della prova assente o non raggiungibile: {value}") from exc
    if not resolved.is_file():
        raise ValueError(f"La prova non identifica un file regolare: {value}")
    return resolved


def _inside(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def _collect_evidence_refs(value, found=None):
    if found is None:
        found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "evidence_refs":
                if not isinstance(item, list):
                    raise ValueError("Il campo evidence_refs deve essere un elenco.")
                found.extend(item)
            else:
                _collect_evidence_refs(item, found)
    elif isinstance(value, list):
        for item in value:
            _collect_evidence_refs(item, found)
    return found


def validate_semantic_proposal(root, proposal):
    """Valida schema, collegamenti alle prove, identità e impronte dei file.

    Restituisce True solo se ogni prova risolve a un file effettivo e la sua
    impronta corrisponde. Non esegue né interpreta il materiale acquisito.
    """
    root = Path(root).resolve()
    if not isinstance(proposal, dict):
        raise ValueError("La proposta semantica deve essere un oggetto JSON.")

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = sorted(validator.iter_errors(proposal), key=lambda error: list(error.absolute_path))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Schema della proposta non disponibile o non valido: {exc}") from exc
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "proposta"
        raise ValueError(f"Proposta non conforme allo schema in {location}: {error.message}")

    evidence = proposal["evidence"]
    evidence_by_id = {}
    for item in evidence:
        evidence_id = item["id"]
        if evidence_id in evidence_by_id:
            raise ValueError(f"Identificativo della prova duplicato: {evidence_id}")
        evidence_by_id[evidence_id] = item

    for reference in _collect_evidence_refs(proposal):
        if reference not in evidence_by_id:
            raise ValueError(f"Il riferimento alla prova è inesistente: {reference}")

    catalog, catalog_path = _load_catalog(root)
    material_id = proposal["material"]["id"]
    record = next(
        (item for item in catalog["materials"]
         if isinstance(item, dict) and item.get("id") == material_id),
        None
    )
    if record is None:
        raise ValueError(f"Materiale non presente nel catalogo: {material_id}")

    acquisition = record.get("acquisition", {})
    original = acquisition.get("original", {})
    if acquisition.get("status") != "preserved" and original.get("kind") != "remote_reference":
        raise ValueError("Il materiale locale non risulta conservato nello stato preserved.")
    if proposal["material"]["original_kind"] != original.get("kind"):
        raise ValueError("Il tipo originale dichiarato nella proposta non corrisponde al catalogo.")

    remote = original.get("kind") == "remote_reference"
    original_digest = original.get("sha256")
    if remote:
        if acquisition.get("status") not in {"received", "preserved"}:
            raise ValueError("Il riferimento remoto non ha uno stato di acquisizione valido.")
        if proposal["material"]["sha256"] is not None:
            raise ValueError("Il riferimento remoto non deve dichiarare un'impronta di file locale.")
        if proposal["status"] != "not_available" or proposal["classification"]["kind"] != "unclassified":
            raise ValueError("Un riferimento remoto non esaminato deve restare not_available e unclassified.")
    else:
        if not isinstance(original_digest, str) or proposal["material"]["sha256"] != original_digest:
            raise ValueError("L'impronta del materiale nella proposta non corrisponde al catalogo.")
        original_path = _record_original_path(root, record)
        if not original_path.exists() or _fingerprint(original_path, original) != original_digest:
            raise ValueError("Il materiale acquisito è stato modificato dopo l'acquisizione.")
        original_path = original_path.resolve()

    catalog_hash = _sha256(catalog_path)
    content_evidence_count = 0
    for item in evidence:
        source = item["source"]
        if source == "catalog/materials.json":
            if item["kind"] != "metadata":
                raise ValueError("Le prove del catalogo devono essere di tipo metadata.")
            if item["sha256"] != catalog_hash:
                raise ValueError("L'impronta della prova catalogo non corrisponde al catalogo corrente.")
            continue

        if not source.startswith("intake/"):
            raise ValueError(f"Sorgente della prova non ammessa: {source}")
        if remote:
            raise ValueError("Un riferimento remoto non esaminato non può avere prove di contenuto locali.")

        evidence_path = _safe_relative_path(root, source)
        intake_root = (root / "intake").resolve()
        if not _inside(evidence_path, intake_root):
            raise ValueError(f"La prova è fuori dalla cartella intake: {source}")
        if original_path.is_file():
            belongs_to_original = evidence_path == original_path
        else:
            belongs_to_original = _inside(evidence_path, original_path)
        if not belongs_to_original:
            raise ValueError(f"La prova è fuori dal materiale acquisito: {source}")
        if item["sha256"] != _sha256(evidence_path):
            raise ValueError(f"L'impronta della prova non corrisponde al file esaminato: {source}")
        content_evidence_count += 1

    if not remote and proposal["status"] == "completed" and proposal["classification"]["kind"] != "unclassified":
        if content_evidence_count == 0:
            raise ValueError("Una classificazione sostanziale completata richiede prove tratte dai file esaminati.")

    if remote and any(item["source"] != "catalog/materials.json" for item in evidence):
        raise ValueError("Le prove del riferimento remoto possono attestare soltanto i metadati di catalogo.")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verifica schema e integrità delle prove di una proposta semantica.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--proposal", type=Path, required=True, help="Percorso del file JSON della proposta.")
    args = parser.parse_args()
    proposal_path = args.proposal if args.proposal.is_absolute() else args.root / args.proposal
    try:
        proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
        validate_semantic_proposal(args.root, proposal)
        print("CONTROLLO SUPERATO: schema, riferimenti, identità e impronte delle prove coerenti.")
        return 0
    except (OSError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"CONTROLLO NON SUPERATO: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
