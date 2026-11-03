#!/usr/bin/env python3
"""Controlli applicativi di integrità delle prove nelle proposte semantiche."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath

from jsonschema import Draft202012Validator, FormatChecker

if __package__ in {None, ""}:
    from material_integrity import load_material_record, verify_material
else:
    from scripts.material_integrity import load_material_record, verify_material


try:
    from scripts.semantic_claim_evidence import validate_claim_evidence
except ImportError:
    from semantic_claim_evidence import validate_claim_evidence


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
    if relative.is_absolute() or any(part in {"", ".", ".."} or ":" in part for part in relative.parts):
        raise ValueError("Percorso della prova non valido o contiene attraversamento di cartelle.")
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"collegamento simbolico non ammesso nel percorso della prova: {value}")
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



def _validate_safe_intake_path(value: str) -> None:
    if not isinstance(value, str) or not value.startswith("intake/"):
        raise ValueError("Il percorso deve essere relativo e rimanere sotto intake/.")
    if "\\" in value or "\x00" in value:
        raise ValueError("Il percorso contiene caratteri non ammessi.")
    relative = PurePosixPath(value)
    if relative.is_absolute() or relative.as_posix() != value:
        raise ValueError("Il percorso non è canonico o è assoluto.")
    if any(part in {"", ".", ".."} or ":" in part for part in relative.parts):
        raise ValueError("Il percorso contiene attraversamento di cartelle o componenti non ammessi.")


def validate_semantic_request(request):
    """Valida schema e coerenza incrociata della richiesta inviata al motore."""
    if not isinstance(request, dict):
        raise ValueError("La richiesta semantica deve essere un oggetto JSON.")
    schema_path = SCHEMA_PATH.with_name("semantic-classification-request.schema.json")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(request), key=lambda error: list(error.absolute_path))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Schema della richiesta non disponibile o non valido: {exc}") from exc
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "richiesta"
        raise ValueError(f"Richiesta non conforme allo schema in {location}: {error.message}")

    limits = request["limits"]
    files_by_path = {}
    total_file_bytes = 0
    for item in request["files"]:
        path = item["path"]
        _validate_safe_intake_path(path)
        if path in files_by_path:
            raise ValueError(f"Percorso file duplicato nella richiesta: {path}")
        if item["size_bytes"] > limits["max_file_bytes"]:
            raise ValueError(f"La dimensione dichiarata del file supera il limite: {path}")
        files_by_path[path] = item
        total_file_bytes += item["size_bytes"]
    if len(files_by_path) > limits["max_files"]:
        raise ValueError("Il numero di file supera il limite dichiarato.")
    if total_file_bytes > limits["max_total_bytes"]:
        raise ValueError("La dimensione complessiva dei file supera il limite dichiarato.")

    total_selected_bytes = 0
    for item in request["selected_content"]:
        path = item["path"]
        _validate_safe_intake_path(path)
        allowed = files_by_path.get(path)
        if allowed is None:
            raise ValueError(f"Il contenuto selezionato non è presente nell'elenco dei file ammessi: {path}")
        if item["sha256"] != allowed["sha256"]:
            raise ValueError(f"L'impronta del contenuto selezionato non corrisponde al file ammesso: {path}")
        actual_size = len(item["text"].encode("utf-8"))
        if actual_size != item["size_bytes"] or actual_size > allowed["size_bytes"]:
            raise ValueError(f"La dimensione del contenuto selezionato non corrisponde ai dati dichiarati: {path}")
        if actual_size > limits["max_file_bytes"]:
            raise ValueError(f"La dimensione del contenuto selezionato supera il limite: {path}")
        total_selected_bytes += actual_size
    if total_selected_bytes > limits["max_total_bytes"]:
        raise ValueError("La dimensione complessiva dei contenuti selezionati supera il limite dichiarato.")

    if request["material"]["original_kind"] == "remote_reference":
        if request["material"]["sha256"] is not None or request["files"] or request["selected_content"]:
            raise ValueError("Un riferimento remoto non visitato non può includere file o contenuti selezionati.")
    elif request["material"]["sha256"] is None:
        raise ValueError("Un materiale locale deve dichiarare l'impronta SHA-256 dell'originale.")
    return True


def _validate_result_status_constraints(proposal):
    status = proposal["status"]
    if status == "partial" and not proposal["limits"]:
        raise ValueError("Una proposta partial deve dichiarare almeno un limite esplicito.")
    if status not in {"not_available", "failed"}:
        return
    if proposal["classification"]["kind"] != "unclassified" or proposal["classification"]["confidence"] != "low":
        raise ValueError("Una proposta not_available o failed deve restare unclassified con confidenza low.")
    if (proposal["capabilities"] or proposal["interfaces"]["inputs"] or
            proposal["interfaces"]["outputs"] or proposal["interfaces"]["usage_conditions"] or
            proposal["dependencies"] or proposal["tools_and_platforms"] or
            proposal["missing_references"] or proposal["contradictions"] or proposal["risks"]):
        raise ValueError("Una proposta not_available o failed non può contenere affermazioni semantiche.")
    if not proposal["unknowns"] or not proposal["limits"]:
        raise ValueError("Una proposta not_available o failed deve dichiarare incognite e limiti.")
    evidence_by_id = {item["id"]: item for item in proposal["evidence"]}
    if not proposal["evidence"] or any(
        item["source"] != "catalog/materials.json" or item["kind"] != "metadata"
        for item in proposal["evidence"]
    ):
        raise ValueError("Una proposta not_available o failed può contenere soltanto prove metadata del catalogo.")
    for reference in proposal["classification"]["evidence_refs"]:
        item = evidence_by_id.get(reference)
        if item is None or item["source"] != "catalog/materials.json" or item["kind"] != "metadata":
            raise ValueError("La classificazione non disponibile può riferirsi soltanto a metadati del catalogo.")

def validate_semantic_proposal(root, proposal):
    """Valida schema, collegamenti alle prove, identità e impronte dei file.

    Restituisce True solo se ogni prova risolve a un file effettivo e la sua
    impronta corrisponde. Non esegue né interpreta il materiale acquisito.
    """
    root = Path(root).resolve()
    if not isinstance(proposal, dict):
        raise ValueError("La proposta semantica deve essere un oggetto JSON.")

    raw_evidence = proposal.get("evidence")
    if isinstance(raw_evidence, list):
        seen_ids = set()
        for item in raw_evidence:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                evidence_id = item["id"]
                if evidence_id in seen_ids:
                    raise ValueError(f"identificativo della prova duplicato: {evidence_id}")
                seen_ids.add(evidence_id)

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

    _validate_result_status_constraints(proposal)
    evidence = proposal["evidence"]
    evidence_by_id = {}
    for item in evidence:
        evidence_id = item["id"]
        if evidence_id in evidence_by_id:
            raise ValueError(f"identificativo della prova duplicato: {evidence_id}")
        evidence_by_id[evidence_id] = item

    for reference in _collect_evidence_refs(proposal):
        if reference not in evidence_by_id:
            raise ValueError(f"Il riferimento alla prova è inesistente: {reference}")

    material_id = proposal["material"]["id"]
    record, catalog, catalog_path = load_material_record(root, material_id)
    acquisition = record.get("acquisition", {})
    original = acquisition.get("original", {})
    if proposal["material"]["original_kind"] != original.get("kind"):
        raise ValueError("Il tipo originale dichiarato nella proposta non corrisponde al catalogo.")

    remote = original.get("kind") == "remote_reference"
    original_digest = original.get("sha256")
    if remote:
        integrity = verify_material(root, material_id, allowed_states=("received", "preserved"))
        if integrity["status"] != "not_applicable":
            problem = integrity["problems"][0]["message"] if integrity["problems"] else "Il riferimento remoto non è verificabile."
            raise ValueError(problem)
        if proposal["material"]["sha256"] is not None:
            raise ValueError("Il riferimento remoto non deve dichiarare un'impronta di file locale.")
        if proposal["status"] != "not_available" or proposal["classification"]["kind"] != "unclassified":
            raise ValueError("Un riferimento remoto non esaminato deve restare not_available e unclassified.")
        if (proposal["capabilities"] or proposal["interfaces"]["inputs"] or
                proposal["interfaces"]["outputs"] or proposal["interfaces"]["usage_conditions"] or
                proposal["dependencies"] or proposal["tools_and_platforms"] or
                proposal["contradictions"] or proposal["risks"]):
            raise ValueError("Un riferimento remoto non esaminato non può contenere affermazioni sul contenuto.")
        original_path = None
    else:
        if acquisition.get("status") != "preserved":
            raise ValueError("Il materiale locale non risulta conservato nello stato preserved.")
        if not isinstance(original_digest, str) or proposal["material"]["sha256"] != original_digest:
            raise ValueError("L'impronta del materiale nella proposta non corrisponde al catalogo.")
        integrity = verify_material(
            root, material_id, expected_digest=original_digest, allowed_states=("preserved",)
        )
        if integrity["status"] != "verified":
            raise ValueError("Il materiale acquisito è stato modificato dopo l'acquisizione.")
        original_path = root / integrity["path"]

    catalog_hash = _sha256(catalog_path)
    content_evidence_count = 0
    for item in evidence:
        source = item["source"]
        if source == "catalog/materials.json":
            if item["kind"] != "metadata":
                raise ValueError("Le prove del catalogo devono essere di tipo metadata.")
            if item["sha256"] != catalog_hash:
                raise ValueError("impronta della prova catalogo non corrisponde al catalogo corrente.")
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
        if item.get("kind") == "text_file":
            try:
                text_content = evidence_path.read_text(encoding="utf-8")
            except (UnicodeError, OSError) as exc:
                raise ValueError(f"La prova dichiarata testuale non è leggibile come UTF-8: {source}") from exc
            if chr(0) in text_content:
                raise ValueError(f"La prova dichiarata testuale contiene byte nulli: {source}")
        if "location" in item:
            try:
                line_count = len(evidence_path.read_text(encoding="utf-8").splitlines())
            except (UnicodeError, OSError) as exc:
                raise ValueError(f"Impossibile verificare le righe della prova: {source}") from exc
            start = item["location"]["start_line"]
            end = item["location"]["end_line"]
            if start > end or end > line_count:
                raise ValueError(f"Intervallo di righe non presente nel file della prova: {source}")
        content_evidence_count += 1

    if not remote and proposal["status"] == "completed" and proposal["classification"]["kind"] != "unclassified":
        if content_evidence_count == 0:
            raise ValueError("Una classificazione sostanziale completata richiede prove tratte dai file esaminati.")

    if remote and any(item["source"] != "catalog/materials.json" for item in evidence):
        raise ValueError("Le prove del riferimento remoto possono attestare soltanto i metadati di catalogo.")

    validate_claim_evidence(root, proposal)

    # Ricontrollo finale per rilevare modifiche avvenute durante la verifica.
    if _sha256(catalog_path) != catalog_hash:
        raise ValueError("Il catalogo è cambiato durante la verifica delle prove.")
    if not remote:
        final_integrity = verify_material(
            root, material_id, expected_digest=original_digest, allowed_states=("preserved",)
        )
        if final_integrity["status"] != "verified":
            raise ValueError("Il materiale è cambiato durante la verifica delle prove.")
    else:
        final_integrity = verify_material(root, material_id, allowed_states=("received", "preserved"))
        if final_integrity["status"] != "not_applicable":
            raise ValueError("Il riferimento remoto è cambiato durante la verifica delle prove.")

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
