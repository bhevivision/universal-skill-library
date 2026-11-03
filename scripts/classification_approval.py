#!/usr/bin/env python3
"""Approvazione esplicita delle proposte di classificazione."""
from __future__ import annotations

import argparse
import jsonschema
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

try:
    from acquire_material import _acquisition_lock
    from material_integrity import _read_catalog, load_material_record, verify_material
except ImportError:
    from scripts.acquire_material import _acquisition_lock
    from scripts.material_integrity import _read_catalog, load_material_record, verify_material


def _is_reparse_point(info):
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(info, "st_file_attributes", 0) & flag)


MAX_PROPOSAL_BYTES = 2 * 1024 * 1024
MAX_EVIDENCE_BYTES = 256 * 1024
PROPOSAL_SCHEMA = "schemas/classification-proposal.schema.json"


def _read_proposal_snapshot(path):
    """Legge una proposta da un descrittore stabile e ne restituisce i byte esatti."""
    before = path.lstat()
    if stat.S_ISLNK(before.st_mode) or _is_reparse_point(before) or not stat.S_ISREG(before.st_mode):
        raise ValueError("La proposta non è un file regolare sicuro.")
    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        identity = (before.st_dev, before.st_ino)
        if not stat.S_ISREG(opened.st_mode) or _is_reparse_point(opened) or (opened.st_dev, opened.st_ino) != identity:
            raise ValueError("La proposta è cambiata durante l'apertura.")
        chunks = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, MAX_PROPOSAL_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_PROPOSAL_BYTES:
                raise ValueError("La proposta supera la dimensione massima consentita.")
        raw = b"".join(chunks)
        after_fd = os.fstat(descriptor)
        after_path = path.lstat()
        if (after_fd.st_dev, after_fd.st_ino) != identity:
            raise ValueError("Il file della proposta è cambiato durante la lettura.")
        if (after_path.st_dev, after_path.st_ino) != identity or stat.S_ISLNK(after_path.st_mode) or _is_reparse_point(after_path):
            raise ValueError("Il percorso della proposta è stato sostituito durante la lettura.")
        if after_fd.st_size != len(raw):
            raise ValueError("La proposta è cambiata durante la lettura.")
        return raw, hashlib.sha256(raw).hexdigest()
    finally:
        os.close(descriptor)


def _read_evidence_snapshot(root, source):
    relative = PurePosixPath(source)
    if (
        not isinstance(source, str) or "\\" in source or "\x00" in source
        or relative.is_absolute() or not relative.parts or relative.parts[0] != "intake"
        or any(part in {"", ".", ".."} or ":" in part for part in relative.parts)
    ):
        raise ValueError("Percorso della prova non valido.")
    path = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or _is_reparse_point(info):
            raise ValueError("La prova contiene un collegamento o punto di reindirizzamento.")
    try:
        path.resolve(strict=True).relative_to((root / "intake").resolve(strict=True))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ValueError("La prova non è contenuta in intake/.") from exc
    raw, digest = _read_proposal_snapshot(path)
    if len(raw) > MAX_EVIDENCE_BYTES:
        raise ValueError("La prova testuale supera il limite massimo consentito.")
    return raw, digest


def _validate_proposal(root, proposal, proposal_id):
    schema_path = root / PROPOSAL_SCHEMA
    schema_info = schema_path.lstat()
    if stat.S_ISLNK(schema_info.st_mode) or _is_reparse_point(schema_info) or not stat.S_ISREG(schema_info.st_mode):
        raise ValueError("Schema della proposta assente o non sicuro.")
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        errors = sorted(validator.iter_errors(proposal), key=lambda item: list(item.absolute_path))
    except (OSError, UnicodeError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        raise ValueError("Schema della proposta non leggibile o non valido.") from exc
    if errors:
        details = "; ".join(
            f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
            for error in errors[:10]
        )
        raise ValueError("Proposta non conforme allo schema: " + details)

    if proposal["proposal_id"] != proposal_id:
        raise ValueError("Identità della proposta non valida.")
    evidence = proposal["evidence"]
    material = proposal["material"]
    if material["original_kind"] == "remote_reference":
        if material["sha256"] is not None or evidence:
            raise ValueError("La proposta remota non deve dichiarare prove locali.")
        return
    identities = [
        item for item in evidence
        if item["type"] == "identity" and item["source"] == "catalog/materials.json"
    ]
    file_evidence = [item for item in evidence if item["type"] == "text_file"]
    if len(identities) != 1:
        raise ValueError("La proposta locale deve contenere una sola prova d'identità del materiale.")
    identity = identities[0]
    if identity["material_id"] != material["id"] or identity["sha256"] != material["sha256"]:
        raise ValueError("La prova d'identità non corrisponde al materiale dichiarato.")
    if proposal["analysis"]["files_examined"] != len(file_evidence):
        raise ValueError("Il numero di prove testuali non coincide con i file dichiarati esaminati.")
    sources = [item["source"] for item in file_evidence]
    if len(sources) != len(set(sources)):
        raise ValueError("La proposta contiene prove duplicate per lo stesso file.")
    for item in file_evidence:
        raw, actual_digest = _read_evidence_snapshot(root, item["source"])
        if item["sha256"] != actual_digest or item["bytes"] != len(raw):
            raise ValueError("Una prova testuale non corrisponde più al file originale.")


ALLOWED_KINDS = {"skill", "tool", "agent", "workflow", "resource", "composite", "unclassified"}


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} obbligatorio.")
    return value.strip()


def _atomic_json_write(path, value):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def decide_proposal(root, proposal_id, *, decision, actor, rationale):
    """Registra una decisione umana sul contenuto esatto e verificato della proposta."""
    root = Path(root).resolve()
    if not isinstance(proposal_id, str) or not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", proposal_id):
        raise ValueError("Identificativo proposta non valido.")
    actor = _required_text(actor, "Responsabile della decisione")
    rationale = _required_text(rationale, "Motivazione della decisione")
    if decision not in {"approved", "rejected"}:
        raise ValueError("Decisione non supportata.")

    lock_path = _acquisition_lock(root)
    try:
        proposals_dir = root / "proposals"
        proposals_info = proposals_dir.lstat()
        if stat.S_ISLNK(proposals_info.st_mode) or _is_reparse_point(proposals_info) or not stat.S_ISDIR(proposals_info.st_mode):
            raise FileNotFoundError("Cartella delle proposte assente o non sicura.")
        proposal_path = proposals_dir / f"{proposal_id}.json"
        proposal_info = proposal_path.lstat()
        if stat.S_ISLNK(proposal_info.st_mode) or _is_reparse_point(proposal_info) or not stat.S_ISREG(proposal_info.st_mode):
            raise FileNotFoundError(f"Proposta non trovata o non sicura: {proposal_id}")
        proposal_bytes, proposal_digest = _read_proposal_snapshot(proposal_path)
        try:
            proposal = json.loads(proposal_bytes.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("La proposta non è un documento JSON UTF-8 valido.") from exc
        if not isinstance(proposal, dict):
            raise ValueError("La proposta deve essere un oggetto JSON.")
        _validate_proposal(root, proposal, proposal_id)

        material = proposal["material"]
        proposed = proposal["proposal"]
        material_id = material["id"]

        catalog_before, catalog_path, catalog_digest = _read_catalog(root)
        record, catalog, loaded_catalog_path = load_material_record(root, material_id)
        if loaded_catalog_path != catalog_path or hashlib.sha256(catalog_path.read_bytes()).hexdigest() != catalog_digest:
            raise ValueError("Il catalogo è cambiato durante il caricamento; decisione bloccata.")
        if catalog != catalog_before:
            raise ValueError("Il catalogo è cambiato durante il caricamento; decisione bloccata.")

        acquisition = record.get("acquisition", {})
        original = acquisition.get("original", {})
        if original.get("kind") != material.get("original_kind"):
            raise ValueError("Il tipo originale nella proposta non corrisponde al record del materiale.")
        if original.get("kind") == "remote_reference":
            integrity = verify_material(root, material_id, allowed_states=("received", "preserved"))
            if integrity["status"] != "not_applicable":
                problem = integrity["problems"][0]["message"] if integrity["problems"] else "Il riferimento remoto non è verificabile."
                raise ValueError(problem)
        else:
            if acquisition.get("status") != "preserved":
                raise ValueError("Il materiale locale non è in stato preserved.")
            integrity = verify_material(
                root, material_id, expected_digest=material.get("sha256"), allowed_states=("preserved",)
            )
            if integrity["status"] != "verified":
                codes = {item["code"] for item in integrity["problems"]}
                if codes.intersection({"DIGEST_MISMATCH", "EXPECTED_DIGEST_MISMATCH"}):
                    if integrity.get("actual_digest") == material.get("sha256"):
                        raise ValueError("La proposta non corrisponde all'impronta registrata nell'acquisizione.")
                    raise ValueError("Il materiale è cambiato dopo l'analisi; decisione bloccata.")
                problem = integrity["problems"][0]["message"] if integrity["problems"] else "Integrità del materiale non verificata."
                raise ValueError(problem)
            if original.get("sha256") != material.get("sha256"):
                raise ValueError("La proposta non corrisponde all'impronta registrata nell'acquisizione.")

        classification = record.setdefault("classification", {"status": "not_examined", "kind": "unclassified"})
        if not isinstance(classification, dict):
            raise ValueError("Scheda di classificazione del materiale non valida.")
        history = classification.setdefault("decisions", [])
        if not isinstance(history, list):
            raise ValueError("Storico delle decisioni non valido.")
        if any(isinstance(item, dict) and item.get("proposal_id") == proposal_id for item in history):
            raise ValueError("Questa proposta ha già una decisione registrata.")

        decision_record = {
            "proposal_id": proposal_id,
            "decision": decision,
            "decided_at": _now(),
            "actor": actor,
            "rationale": rationale,
            "material_sha256": material.get("sha256"),
            "proposal_sha256": proposal_digest,
            "proposed_kind": proposed["kind"]
        }
        history.append(decision_record)

        if decision == "approved":
            if proposed["kind"] == "unclassified":
                classification.update({"status": "unclassified", "kind": "unclassified"})
            else:
                classification.update({
                    "status": "classified",
                    "kind": proposed["kind"],
                    "confidence": proposed["confidence"],
                    "rationale": proposed["rationale"]
                })
        elif classification.get("status") != "classified":
            classification.update({"status": "unclassified", "kind": "unclassified", "rationale": rationale})

        current_proposal, current_proposal_digest = _read_proposal_snapshot(proposal_path)
        if current_proposal_digest != proposal_digest or current_proposal != proposal_bytes:
            raise ValueError("La proposta è cambiata durante la decisione; operazione bloccata.")
        current_catalog, current_catalog_path, current_catalog_digest = _read_catalog(root)
        if current_catalog_path != catalog_path or current_catalog_digest != catalog_digest or current_catalog != catalog_before:
            raise ValueError("Il catalogo è cambiato durante la decisione; operazione bloccata.")
        _atomic_json_write(catalog_path, catalog)
        return {"material_id": material_id, "proposal_id": proposal_id, **decision_record}
    finally:
        lock_path.unlink(missing_ok=True)


def approve_proposal(root, proposal_id, *, actor, rationale):
    return decide_proposal(root, proposal_id, decision="approved", actor=actor, rationale=rationale)


def reject_proposal(root, proposal_id, *, actor, rationale):
    return decide_proposal(root, proposal_id, decision="rejected", actor=actor, rationale=rationale)


def main():
    parser = argparse.ArgumentParser(description="Approva o respinge una proposta senza creare o abilitare una skill.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--proposal-id", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--decision", choices=("approve", "reject"), required=True)
    args = parser.parse_args()
    try:
        operation = approve_proposal if args.decision == "approve" else reject_proposal
        result = operation(args.root, args.proposal_id, actor=args.actor, rationale=args.reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"DECISIONE NON REGISTRATA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
