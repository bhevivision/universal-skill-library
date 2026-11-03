#!/usr/bin/env python3
"""Normalizzazione prudente delle risposte del modello e verifica delle citazioni."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("La risposta JSON contiene una chiave duplicata.")
        result[key] = value
    return result


def _decode_object(candidate: str):
    try:
        value = json.loads(candidate, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError("La risposta del modello contiene JSON incompleto o malformato.") from exc
    if not isinstance(value, dict):
        raise ValueError("La risposta del modello deve essere un oggetto JSON.")
    return value


def normalize_model_json(content):
    """Accetta JSON puro, blocchi Markdown o testo circostante; non ripara dati troncati."""
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Risposta del modello vuota o non testuale.")
    raw = content.strip()
    if raw.startswith("{") and raw.endswith("}"):
        return _decode_object(raw)

    fenced = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.IGNORECASE | re.DOTALL)
    if len(fenced) == 1:
        return _decode_object(fenced[0])
    if len(fenced) > 1:
        raise ValueError("La risposta contiene più blocchi JSON: selezione ambigua.")

    # Estrae un solo oggetto bilanciato senza confondere parentesi dentro stringhe.
    start = raw.find("{")
    if start < 0:
        raise ValueError("Nessun oggetto JSON trovato nella risposta del modello.")
    depth = 0
    in_string = False
    escaped = False
    end = None
    for index in range(start, len(raw)):
        char = raw[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end is None or depth != 0 or in_string:
        raise ValueError("La risposta del modello contiene un oggetto JSON incompleto.")
    if raw[end:].find("{") >= 0:
        raise ValueError("La risposta contiene più oggetti JSON: selezione ambigua.")
    return _decode_object(raw[start:end])


def _safe_source(root: Path, source: str) -> Path:
    if not isinstance(source, str) or not source.startswith("intake/") or "\\" in source or "\x00" in source:
        raise ValueError("Sorgente della citazione non valida.")
    relative = PurePosixPath(source)
    if relative.is_absolute() or relative.as_posix() != source or any(part in {"", ".", ".."} or ":" in part for part in relative.parts):
        raise ValueError("Percorso della citazione non sicuro.")
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("I collegamenti simbolici non sono ammessi nelle prove.")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_file() or not resolved.is_relative_to((root / "intake").resolve()):
        raise ValueError("La citazione non punta a un file sorgente ammesso.")
    return resolved


def _claim_text_fields(proposal):
    """Restituisce i testi che costituiscono affermazioni semantiche."""
    classification = proposal.get("classification")
    if isinstance(classification, dict) and classification.get("kind") != "unclassified":
        for field in ("rationale", "summary"):
            yield classification, field

    for collection in ("capabilities", "dependencies", "tools_and_platforms", "contradictions", "risks"):
        values = proposal.get(collection, [])
        if not isinstance(values, list):
            raise ValueError(f"{collection} deve essere un elenco.")
        fields = {
            "capabilities": ("name", "description"),
            "dependencies": ("name",),
            "tools_and_platforms": ("name",),
            "contradictions": ("description",),
            "risks": ("description",),
        }[collection]
        for item in values:
            if not isinstance(item, dict):
                raise ValueError(f"Voce non valida in {collection}.")
            for field in fields:
                yield item, field

    interfaces = proposal.get("interfaces", {})
    if not isinstance(interfaces, dict):
        raise ValueError("interfaces deve essere un oggetto.")
    for group in ("inputs", "outputs", "usage_conditions"):
        values = interfaces.get(group, [])
        if not isinstance(values, list):
            raise ValueError(f"interfaces.{group} deve essere un elenco.")
        for item in values:
            if not isinstance(item, dict) or "value" not in item:
                raise ValueError(f"Affermazione non valida in interfaces.{group}.")
            yield item, "value"


def validate_claim_evidence(root, proposal, allowed_sources=None):
    """Ogni testo assertivo deve avere citazioni esatte in file con SHA-256 verificato."""
    root = Path(root).resolve()
    if not isinstance(proposal, dict):
        raise ValueError("La proposta deve essere un oggetto.")
    evidence = proposal.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("Elenco delle prove assente o non valido.")
    by_id = {}
    for item in evidence:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Voce prova non valida.")
        if item["id"] in by_id:
            raise ValueError("Identificativo della prova duplicato.")
        by_id[item["id"]] = item

    checked_files = {}
    claims = list(_claim_text_fields(proposal))
    for claim, field in claims:
        text = claim.get(field)
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Affermazione vuota o malformata: {field}.")
        refs = claim.get("evidence_refs")
        quotes = claim.get("evidence_quotes")
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) for ref in refs):
            raise ValueError(f"Affermazione senza riferimenti validi: {field}.")
        if not isinstance(quotes, list) or not quotes:
            raise ValueError(f"Affermazione senza citazioni testuali: {field}.")
        cited = set()
        for quote_item in quotes:
            if not isinstance(quote_item, dict):
                raise ValueError("Citazione testuale malformata.")
            ref = quote_item.get("evidence_ref")
            quote = quote_item.get("quote")
            if ref not in refs or ref not in by_id:
                raise ValueError("La citazione non è collegata a un riferimento prova dell'affermazione.")
            if not isinstance(quote, str) or not quote.strip():
                raise ValueError("Citazione testuale vuota o non valida.")
            item = by_id[ref]
            if item.get("kind") != "text_file":
                raise ValueError("Le affermazioni richiedono prove da file testuali.")
            source = item.get("source")
            if allowed_sources is not None and (source not in allowed_sources or allowed_sources[source] != item.get("sha256")):
                raise ValueError("La prova non corrisponde a un file selezionato e autorizzato nella richiesta.")
            if source not in checked_files:
                path = _safe_source(root, source)
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != item.get("sha256"):
                    raise ValueError(f"Impronta SHA-256 non corrispondente: {source}")
                try:
                    checked_files[source] = (digest, path.read_text(encoding="utf-8"))
                except UnicodeError as exc:
                    raise ValueError(f"File sorgente non UTF-8: {source}") from exc
            elif checked_files[source][0] != item.get("sha256"):
                raise ValueError(f"Impronta SHA-256 non corrispondente: {source}")
            if quote not in checked_files[source][1]:
                raise ValueError(f"Citazione inventata o assente nel file sorgente: {source}")
            cited.add(ref)
        if not cited or set(refs) - cited:
            raise ValueError(f"Nessuna citazione valida per tutti i riferimenti dell'affermazione: {field}.")

    if proposal.get("status") == "completed":
        if proposal.get("missing_references") or proposal.get("contradictions") or proposal.get("unknowns") or proposal.get("limits"):
            raise ValueError("completed non ammesso: restano riferimenti mancanti, contraddizioni, incognite o limiti.")
        if not claims:
            raise ValueError("completed non ammesso senza affermazioni semantiche verificate.")
    return True


__all__ = ["normalize_model_json", "validate_claim_evidence"]
