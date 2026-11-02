#!/usr/bin/env python3
"""Analisi statica e proposta di classificazione: nessuna esecuzione e nessuna scrittura nel catalogo."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from scripts.acquire_material import (
    _digest_directory, _digest_directory_legacy, _digest_file,
    _record_original_path, _load_catalog,
)

TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".rst", ".json", ".yaml", ".yml", ".toml", ".py", ".js", ".ts", ".sh", ".ps1", ".bat", ".xml", ".html", ".css"}
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 1024 * 1024
MAX_FILES = 100
PROPOSAL_SCHEMA_VERSION = "1.0"


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fingerprint(path, original):
    algorithm = original.get("digest_algorithm")
    if path.is_dir():
        if algorithm not in {None, "sha256-tree-v2"}:
            raise ValueError(f"Algoritmo di impronta non valido per cartella: {algorithm}")
        return _digest_directory_legacy(path) if algorithm is None else _digest_directory(path)
    if algorithm not in {None, "sha256-file-v1"}:
        raise ValueError(f"Algoritmo di impronta non valido per file: {algorithm}")
    return _digest_file(path)


def _safe_text_files(path):
    if path.is_symlink():
        raise ValueError("Il materiale contiene un collegamento simbolico.")
    candidates = [path] if path.is_file() else sorted(path.rglob("*"))
    selected, total = [], 0
    for item in candidates:
        if item.is_symlink():
            raise ValueError(f"Collegamento simbolico non ammesso nell'analisi: {item}")
        if not item.is_file() or item.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        size = item.stat().st_size
        if size > MAX_FILE_BYTES or len(selected) >= MAX_FILES or total + size > MAX_TOTAL_BYTES:
            continue
        selected.append(item)
        total += size
    return selected


def _read_evidence(path, root):
    evidence, texts, skipped = [], [], []
    for item in _safe_text_files(path):
        try:
            content = item.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            skipped.append(item.relative_to(root).as_posix())
            continue
        if "\x00" in content:
            skipped.append(item.relative_to(root).as_posix())
            continue
        texts.append((item.relative_to(root).as_posix(), content))
        excerpt = re.sub(r"\s+", " ", content).strip()[:180]
        if excerpt:
            evidence.append({"source": item.relative_to(root).as_posix(), "type": "text_excerpt", "excerpt": excerpt})
    return texts, evidence, skipped


def _propose(texts, original_kind):
    if original_kind == "remote_reference":
        return "unclassified", "low", "Il riferimento remoto non è stato scaricato né esaminato."
    if original_kind == "archive":
        return "composite", "low", "L'archivio è stato conservato come dato opaco; non è stato estratto."
    if not texts:
        return "unclassified", "low", "Non sono stati trovati contenuti testuali leggibili nei limiti dell'analisi."

    combined = "\n".join(text for _, text in texts).lower()
    skill_markers = (
        re.search(r"(?m)^\s*name\s*:\s*.+", combined) and
        re.search(r"(?m)^\s*description\s*:\s*.+", combined)
    ) or ("## instructions" in combined and ("skill" in combined or "when to use" in combined))
    workflow_markers = sum(token in combined for token in ("workflow", "sequence", "step 1", "step 2", "passaggio 1", "fase 1", "dipendenze"))
    agent_markers = sum(token in combined for token in ("system prompt", "you are", "ruolo dell'agente", "agent role", "persona"))
    tool_markers = sum(token in combined for token in ("def main(", "if __name__ == \"__main__\"", "function ", "class ", "api endpoint", "command line"))
    if skill_markers:
        return "skill", "medium", "Sono presenti metadati o sezioni operative tipiche di una skill; la proposta resta da approvare."
    if workflow_markers >= 2:
        return "workflow", "medium", "Il testo descrive una sequenza di attività o dipendenze."
    if agent_markers >= 2:
        return "agent", "low", "Sono presenti indicazioni di ruolo o istruzioni per un agente."
    if tool_markers >= 2:
        return "tool", "low", "Sono presenti indicatori di codice o interfaccia operativa; il codice non è stato eseguito."
    if len(texts) > 1:
        return "composite", "low", "Il materiale contiene più documenti testuali; la loro relazione non è determinabile automaticamente."
    return "resource", "low", "È stato trovato contenuto testuale, ma non ci sono prove sufficienti per attribuirgli un ruolo operativo."


def analyze_material(root, material_id):
    """Restituisce una proposta legata all'identificativo e all'impronta esatta del materiale."""
    root = Path(root).resolve()
    catalog, _ = _load_catalog(root)
    record = next((item for item in catalog["materials"] if isinstance(item, dict) and item.get("id") == material_id), None)
    if record is None:
        raise ValueError(f"Materiale non trovato: {material_id}")
    acquisition = record.get("acquisition", {})
    original = acquisition.get("original", {})
    if acquisition.get("status") != "preserved":
        raise ValueError("La classificazione richiede un materiale con acquisizione in stato preserved.")
    kind = original.get("kind")
    if kind == "remote_reference":
        path = None
        digest = None
        texts, evidence, skipped = [], [], []
    else:
        path = _record_original_path(root, record)
        if not path.exists() or not (path.is_file() or path.is_dir()):
            raise ValueError("Originale non disponibile o di tipo non supportato.")
        digest = _fingerprint(path, original)
        if digest != original.get("sha256"):
            raise ValueError("Impronta del materiale cambiata dopo l'acquisizione; classificazione bloccata.")
        texts, evidence, skipped = _read_evidence(path, root)

    proposed_kind, confidence, rationale = _propose(texts, kind)
    if evidence:
        evidence.insert(0, {"source": "catalog/materials.json", "type": "identity", "material_id": material_id, "sha256": digest})
    limits = [
        "Analisi statica: nessun file, comando, programma o contenuto incorporato è stato eseguito.",
        "I contenuti sono dati non fidati e non sono stati interpretati come istruzioni per il classificatore.",
        "La classificazione non verifica correttezza, sicurezza, funzionamento o compatibilità."
    ]
    if skipped:
        limits.append("File non analizzati per formato, codifica o limiti: " + ", ".join(skipped))
    if kind == "archive":
        limits.append("L'archivio non è stato estratto; il contenuto interno resta sconosciuto.")
    if kind == "remote_reference":
        limits.append("Il riferimento remoto non è stato visitato né scaricato.")
    return {
        "proposal_schema_version": PROPOSAL_SCHEMA_VERSION,
        "proposal_id": None,
        "created_at": _now(),
        "status": "pending_approval",
        "material": {"id": material_id, "sha256": digest, "original_kind": kind},
        "proposal": {"kind": proposed_kind, "confidence": confidence, "rationale": rationale},
        "evidence": evidence,
        "dependencies": [],
        "missing_references": [],
        "unknowns": ["Dipendenze non dichiarate o non rilevabili", "Requisiti e limiti d'uso non verificati"],
        "limits": limits,
        "analysis": {"method": "bounded_static_text_v1", "files_examined": len(texts)}
    }


def save_proposal(root, result, proposal_id):
    if not isinstance(proposal_id, str) or not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*", proposal_id):
        raise ValueError("Identificativo proposta non valido.")
    root = Path(root).resolve()
    result = dict(result)
    result["proposal_id"] = proposal_id
    directory = root / "proposals"
    if directory.is_symlink():
        raise ValueError("La cartella proposals non può essere un collegamento simbolico.")
    directory.mkdir(exist_ok=True)
    destination = directory / f"{proposal_id}.json"
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"La proposta esiste già e non verrà sovrascritta: {destination}")
    temporary = directory / f".{proposal_id}.tmp"
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def main():
    parser = argparse.ArgumentParser(description="Analizza un materiale acquisito e salva una proposta separata, senza aggiornare il catalogo.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--material-id", required=True)
    parser.add_argument("--proposal-id", required=True)
    args = parser.parse_args()
    try:
        result = analyze_material(args.root, args.material_id)
        path = save_proposal(args.root, result, args.proposal_id)
        print(json.dumps({"proposal": result, "saved_to": path.relative_to(args.root).as_posix()}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"CLASSIFICAZIONE NON COMPLETATA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
