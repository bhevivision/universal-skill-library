#!/usr/bin/env python3
"""Diagnostica temporanea e facoltativa dell'adattatore semantico."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path


_ALLOWED_STAGES = {
    "request",
    "raw_http_response",
    "raw_model_content",
    "parsed_model_json",
    "normalized_output",
    "validation_error",
}


def write_diagnostic(stage: str, request_id: str, payload):
    """Scrive una fase solo se è configurata una cartella diagnostica esplicita."""
    directory = os.environ.get("SEMANTIC_ADAPTER_DIAGNOSTICS_DIR")
    if not directory:
        return None
    if stage not in _ALLOWED_STAGES:
        raise ValueError("Fase diagnostica non ammessa.")
    if not isinstance(request_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", request_id):
        raise ValueError("Identificativo richiesta non valido per la diagnostica.")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    safe_id = re.sub(r"[^A-Za-z0-9._-]", "-", request_id)
    destination = root / f"{safe_id}.{stage}.json"
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    document = {"stage": stage, "request_id": request_id, "payload": payload}
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return destination
