#!/usr/bin/env python3
"""Approvazione esplicita delle proposte di classificazione."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    from material_integrity import load_material_record, verify_material
else:
    from scripts.material_integrity import load_material_record, verify_material


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
    """Registra una decisione umana nel record del materiale, senza creare una skill."""
    root = Path(root).resolve()
    if not isinstance(proposal_id, str) or not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", proposal_id):
        raise ValueError("Identificativo proposta non valido.")
    actor = _required_text(actor, "Responsabile della decisione")
    rationale = _required_text(rationale, "Motivazione della decisione")
    if decision not in {"approved", "rejected"}:
        raise ValueError("Decisione non supportata.")

    proposals_dir = root / "proposals"
    if proposals_dir.is_symlink() or not proposals_dir.is_dir():
        raise FileNotFoundError("Cartella delle proposte assente o non sicura.")
    proposal_path = proposals_dir / f"{proposal_id}.json"
    if proposal_path.is_symlink() or not proposal_path.is_file():
        raise FileNotFoundError(f"Proposta non trovata o non sicura: {proposal_id}")
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    if not isinstance(proposal, dict) or proposal.get("proposal_id") != proposal_id:
        raise ValueError("Identità della proposta non valida.")
    if proposal.get("status") != "pending_approval":
        raise ValueError("La proposta non è in attesa di approvazione.")
    material = proposal.get("material")
    proposed = proposal.get("proposal")
    if not isinstance(material, dict) or not isinstance(proposed, dict):
        raise ValueError("La proposta non contiene i dati di materiale e classificazione richiesti.")
    material_id = material.get("id")
    if not isinstance(material_id, str) or not material_id:
        raise ValueError("Identificativo del materiale mancante nella proposta.")
    proposed_kind = proposed.get("kind")
    if proposed_kind not in ALLOWED_KINDS:
        raise ValueError(f"Categoria proposta non riconosciuta: {proposed_kind}")
    if proposed.get("confidence", "low") not in {"low", "medium", "high"}:
        raise ValueError("Livello di confidenza della proposta non valido.")
    if not isinstance(proposed.get("rationale"), str):
        raise ValueError("Motivazione della proposta mancante o non valida.")

    record, catalog, catalog_path = load_material_record(root, material_id)
    acquisition = record.get("acquisition", {})
    original = acquisition.get("original", {})
    if original.get("kind") == "remote_reference":
        integrity = verify_material(root, material_id, allowed_states=("received", "preserved"))
        if integrity["status"] != "not_applicable":
            problem = integrity["problems"][0]["message"] if integrity["problems"] else "Il riferimento remoto non è verificabile."
            raise ValueError(problem)
        if material.get("sha256") is not None:
            raise ValueError("La proposta remota contiene un'impronta locale inattesa.")
    else:
        if acquisition.get("status") != "preserved":
            raise ValueError("Il materiale locale non è in stato preserved.")
        integrity = verify_material(
            root, material_id, expected_digest=material.get("sha256"), allowed_states=("preserved",)
        )
        if integrity["status"] != "verified":
            codes = {item["code"] for item in integrity["problems"]}
            if "DIGEST_MISMATCH" in codes:
                raise ValueError("Il materiale è cambiato dopo l'analisi; decisione bloccata.")
            if "EXPECTED_DIGEST_MISMATCH" in codes:
                raise ValueError("La proposta non corrisponde all'impronta registrata nell'acquisizione.")
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
