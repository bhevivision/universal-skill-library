#!/usr/bin/env python3
"""Approvazione esplicita delle proposte di classificazione."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.classify_material import _fingerprint, _load_catalog, _record_original_path


ALLOWED_KINDS = {"skill", "tool", "agent", "workflow", "resource", "composite", "unclassified"}


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} obbligatorio.")
    return value.strip()


def _atomic_json_write(path, value):
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"File temporaneo già presente: {temporary}")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def decide_proposal(root, proposal_id, *, decision, actor, rationale):
    """Registra una decisione umana nel record del materiale, senza creare una skill."""
    root = Path(root).resolve()
    if not isinstance(proposal_id, str) or not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", proposal_id):
        raise ValueError("Identificativo proposta non valido.")
    actor = _required_text(actor, "Responsabile della decisione")
    rationale = _required_text(rationale, "Motivazione della decisione")
    if decision not in {"approved", "rejected"}:
        raise ValueError("Decisione non supportata.")

    proposal_path = root / "proposals" / f"{proposal_id}.json"
    if proposal_path.is_symlink() or not proposal_path.is_file():
        raise FileNotFoundError(f"Proposta non trovata o non sicura: {proposal_id}")
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    if not isinstance(proposal, dict) or proposal.get("proposal_id") != proposal_id:
        raise ValueError("Identità della proposta non valida.")
    if proposal.get("status") != "pending_approval":
        raise ValueError("La proposta non è in attesa di approvazione.")
    material = proposal.get("material", {})
    proposed = proposal.get("proposal", {})
    material_id = material.get("id")
    proposed_kind = proposed.get("kind")
    if proposed_kind not in ALLOWED_KINDS:
        raise ValueError(f"Categoria proposta non riconosciuta: {proposed_kind}")

    catalog, catalog_path = _load_catalog(root)
    record = next((item for item in catalog["materials"] if isinstance(item, dict) and item.get("id") == material_id), None)
    if record is None:
        raise ValueError("Il materiale collegato alla proposta non è più presente nel catalogo.")
    original = record.get("acquisition", {}).get("original", {})
    if original.get("kind") == "remote_reference":
        if material.get("sha256") is not None:
            raise ValueError("La proposta remota contiene un'impronta locale inattesa.")
    else:
        current_path = _record_original_path(root, record)
        if not current_path.exists() or _fingerprint(current_path, original) != material.get("sha256"):
            raise ValueError("Il materiale è cambiato dopo l'analisi; decisione bloccata.")
        if original.get("sha256") != material.get("sha256"):
            raise ValueError("La proposta non corrisponde all'impronta registrata nell'acquisizione.")

    classification = record.setdefault("classification", {"status": "not_examined", "kind": "unclassified"})
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
        "proposed_kind": proposed_kind
    }
    history.append(decision_record)

    if decision == "approved":
        if proposed_kind == "unclassified":
            classification.update({"status": "unclassified", "kind": "unclassified"})
        else:
            classification.update({
                "status": "classified",
                "kind": proposed_kind,
                "confidence": proposed.get("confidence", "low"),
                "rationale": proposed.get("rationale", "")
            })
    elif classification.get("status") != "classified":
        classification.update({"status": "unclassified", "kind": "unclassified", "rationale": rationale})

    _atomic_json_write(catalog_path, catalog)
    return {"material_id": material_id, "proposal_id": proposal_id, **decision_record}


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
