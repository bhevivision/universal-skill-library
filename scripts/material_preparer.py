#!/usr/bin/env python3
"""Preparazione in sola lettura dei contenuti testuali di un materiale acquisito."""
from __future__ import annotations

import hashlib
from pathlib import Path

if __package__ in {None, ""}:
    from material_integrity import MaterialIntegrityError, load_material_record, verify_material
else:
    from scripts.material_integrity import MaterialIntegrityError, load_material_record, verify_material


SCHEMA_VERSION = "1.0"
PROFILE = "bounded_text_v1"
TEXT_EXTENSIONS = {
    ".md", ".markdown", ".txt", ".rst", ".json", ".yaml", ".yml",
    ".toml", ".py", ".js", ".ts", ".sh", ".ps1", ".bat", ".xml",
    ".html", ".css",
}
MAX_FILE_BYTES = 256 * 1024
MAX_TOTAL_BYTES = 1024 * 1024
MAX_FILES = 100

_BLOCKING_CODES = {
    "MATERIAL_NOT_FOUND", "DUPLICATE_MATERIAL_ID", "INVALID_RECORD",
    "INVALID_ACQUISITION_STATE", "INVALID_ORIGINAL_PATH", "PATH_OUTSIDE_INTAKE",
    "SYMLINK_NOT_ALLOWED", "ORIGINAL_NOT_FOUND", "DIGEST_MISMATCH",
    "EXPECTED_DIGEST_MISMATCH", "CATALOG_CHANGED_DURING_CHECK",
    "DIGEST_CHANGED_DURING_CHECK",
}


def _problem(code: str, message: str) -> dict:
    return {"code": code, "message": message}


def _base_result(material_id: str, original_kind=None, digest=None, status="failed") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "material": {
            "id": material_id,
            "original_kind": original_kind,
            "sha256": digest,
        },
        "profile": PROFILE,
        "files": [],
        "skipped": [],
        "summary": {
            "files_examined": 0,
            "files_skipped": 0,
            "total_bytes": 0,
        },
        "problems": [],
    }


def _integrity_status(integrity: dict) -> str:
    if integrity.get("status") == "blocked":
        return "blocked"
    if integrity.get("status") == "failed":
        codes = {item.get("code") for item in integrity.get("problems", [])}
        return "blocked" if codes & _BLOCKING_CODES else "failed"
    return "failed"


def _copy_problems(integrity: dict) -> list[dict]:
    problems = integrity.get("problems")
    if not isinstance(problems, list):
        return [_problem("INTEGRITY_CHECK_FAILED", "Il servizio d'integrità ha restituito un risultato non valido.")]
    copied = []
    for item in problems:
        if isinstance(item, dict) and isinstance(item.get("code"), str) and isinstance(item.get("message"), str):
            copied.append(_problem(item["code"], item["message"]))
    return copied or [_problem("INTEGRITY_CHECK_FAILED", "Il controllo d'integrità non è stato completato.")]


def _failed_result(result: dict, status: str, problems: list[dict]) -> dict:
    result["status"] = status
    result["problems"] = problems
    # Un risultato bloccato o fallito non deve esporre contenuti parziali.
    result["files"] = []
    result["skipped"] = []
    result["summary"] = {
        "files_examined": 0,
        "files_skipped": 0,
        "total_bytes": 0,
    }
    return result


def _inventory(path: Path) -> list[Path]:
    if path.is_symlink():
        raise MaterialIntegrityError("SYMLINK_NOT_ALLOWED", "Il materiale contiene un collegamento simbolico.")
    if path.is_file():
        return [path]
    # Materializza l'inventario: un errore esplicito non deve produrre un elenco parziale.
    return sorted(path.rglob("*"))


def _relative_source(item: Path, root: Path) -> str:
    relative = item.relative_to(root).as_posix()
    if not relative.startswith("intake/"):
        raise MaterialIntegrityError(
            "INVALID_ORIGINAL_PATH",
            "Il percorso di un file preparato non rimane sotto intake/.",
        )
    return relative


def prepare_material(root, material_id: str) -> dict:
    """Prepara in memoria i file testuali di un materiale acquisito e verificato."""
    root = Path(root).resolve()
    try:
        record, _catalog, _catalog_path = load_material_record(root, material_id)
    except MaterialIntegrityError as exc:
        status = "blocked" if exc.code in _BLOCKING_CODES else "failed"
        result = _base_result(material_id)
        return _failed_result(result, status, [_problem(exc.code, str(exc))])
    except (OSError, UnicodeError, RuntimeError, TypeError, ValueError) as exc:
        result = _base_result(material_id)
        return _failed_result(result, "failed", [_problem("MATERIAL_LOOKUP_FAILED", str(exc))])

    acquisition = record.get("acquisition")
    original = acquisition.get("original") if isinstance(acquisition, dict) else None
    if not isinstance(original, dict):
        result = _base_result(material_id)
        return _failed_result(
            result, "blocked",
            [_problem("INVALID_RECORD", "Sezione acquisition.original assente o non valida.")],
        )
    original_kind = original.get("kind")
    is_remote = original_kind == "remote_reference"

    integrity = verify_material(
        root,
        material_id,
        allowed_states=("received", "preserved") if is_remote else ("preserved",),
    )
    result = _base_result(
        material_id,
        original_kind=original_kind,
        digest=None if is_remote else integrity.get("actual_digest"),
    )

    if is_remote:
        if integrity.get("status") != "not_applicable":
            return _failed_result(result, _integrity_status(integrity), _copy_problems(integrity))
        # Il riferimento remoto è identificato, ma il suo contenuto non viene visitato.
        result["status"] = "not_available"
        return result

    if integrity.get("status") != "verified":
        return _failed_result(result, _integrity_status(integrity), _copy_problems(integrity))

    material_path = root / integrity["path"]
    expected_digest = integrity.get("actual_digest")

    try:
        candidates = _inventory(material_path)
        selected: list[Path] = []
        skipped: list[dict] = []
        selected_bytes = 0

        for item in candidates:
            if item.is_symlink():
                raise MaterialIntegrityError(
                    "SYMLINK_NOT_ALLOWED",
                    f"Collegamento simbolico non ammesso nell'inventario: {item.relative_to(root).as_posix()}",
                )
            if not item.is_file():
                continue

            source = _relative_source(item, root)
            if item.suffix.lower() not in TEXT_EXTENSIONS:
                skipped.append({"source": source, "reason": "unsupported_extension"})
                continue

            size = item.stat().st_size
            if size > MAX_FILE_BYTES:
                skipped.append({"source": source, "reason": "file_too_large"})
            elif len(selected) >= MAX_FILES:
                skipped.append({"source": source, "reason": "max_files_reached"})
            elif selected_bytes + size > MAX_TOTAL_BYTES:
                skipped.append({"source": source, "reason": "total_size_limit"})
            else:
                selected.append(item)
                selected_bytes += size

        prepared = []
        for item in selected:
            source = _relative_source(item, root)
            try:
                raw = item.read_bytes()
            except OSError:
                skipped.append({"source": source, "reason": "read_error"})
                continue
            try:
                content = raw.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                skipped.append({"source": source, "reason": "invalid_utf8"})
                continue
            if "\x00" in content:
                skipped.append({"source": source, "reason": "nul_byte"})
                continue

            prepared.append({
                "source": source,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "line_count": len(content.splitlines()),
                "content": content,
            })

    except MaterialIntegrityError as exc:
        status = "blocked" if exc.code in _BLOCKING_CODES else "failed"
        return _failed_result(result, status, [_problem(exc.code, str(exc))])
    except (OSError, RuntimeError, ValueError) as exc:
        return _failed_result(
            result, "failed",
            [_problem("INVENTORY_FAILED", f"Impossibile completare l'inventario del materiale: {exc}")],
        )

    # Ricontrollo indipendente dopo la lettura; nessun contenuto è restituito se l'originale è cambiato.
    final_integrity = verify_material(
        root,
        material_id,
        expected_digest=expected_digest,
        allowed_states=("preserved",),
    )
    if final_integrity.get("status") != "verified":
        return _failed_result(
            result,
            _integrity_status(final_integrity),
            _copy_problems(final_integrity),
        )

    result["files"] = prepared
    result["skipped"] = skipped
    result["summary"] = {
        "files_examined": len(prepared),
        "files_skipped": len(skipped),
        "total_bytes": sum(item["bytes"] for item in prepared),
    }
    if not prepared:
        result["status"] = "not_available"
    elif skipped:
        result["status"] = "partial"
    else:
        result["status"] = "completed"
    return result


__all__ = ["prepare_material"]
