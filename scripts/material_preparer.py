#!/usr/bin/env python3
"""Preparazione in sola lettura dei contenuti testuali di un materiale acquisito."""
from __future__ import annotations

import hashlib
import os
import stat
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
MAX_INVENTORY_ENTRIES = 10000
MAX_INVENTORY_DEPTH = 64

_BLOCKING_CODES = {
    "MATERIAL_NOT_FOUND", "DUPLICATE_MATERIAL_ID", "INVALID_RECORD", "INVENTORY_LIMIT_EXCEEDED", "NON_REGULAR_ENTRY",
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
        if isinstance(item, dict) and isinstance(item.get("code"), str):
            # Il servizio comune può includere percorsi locali nei messaggi:
            # il risultato pubblico conserva il codice, non i dettagli del file system.
            copied.append(_problem(
                item["code"],
                f"Il servizio d'integrità ha segnalato il problema {item['code']}.",
            ))
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


def _is_reparse_point(info) -> bool:
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(info, "st_file_attributes", 0) & flag)


def _inventory(path: Path) -> list[Path]:
    root_info = path.lstat()
    if stat.S_ISLNK(root_info.st_mode) or _is_reparse_point(root_info):
        raise MaterialIntegrityError("SYMLINK_NOT_ALLOWED", "Il materiale contiene un collegamento o punto di reindirizzamento.")
    if stat.S_ISREG(root_info.st_mode):
        return [path]
    if not stat.S_ISDIR(root_info.st_mode):
        raise MaterialIntegrityError("NON_REGULAR_ENTRY", "Il materiale non è un file o una cartella regolare.")
    entries = []
    pending = [(path, 0)]
    while pending:
        current, depth = pending.pop()
        children = []
        with os.scandir(current) as iterator:
            for entry in iterator:
                children.append(entry)
                if len(entries) + len(children) > MAX_INVENTORY_ENTRIES:
                    raise MaterialIntegrityError(
                        "INVENTORY_LIMIT_EXCEEDED",
                        "Numero massimo di elementi nell'inventario superato."
                    )
        children.sort(key=lambda item: item.name)
        subdirectories = []
        for entry in children:
            child = Path(entry.path)
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode) or _is_reparse_point(info):
                raise MaterialIntegrityError(
                    "SYMLINK_NOT_ALLOWED", "Il materiale contiene un collegamento simbolico."
                )
            if stat.S_ISDIR(info.st_mode):
                if depth + 1 > MAX_INVENTORY_DEPTH:
                    raise MaterialIntegrityError(
                        "INVENTORY_LIMIT_EXCEEDED",
                        "Profondità massima dell'inventario superata."
                    )
                entries.append(child)
                subdirectories.append((child, depth + 1))
            elif stat.S_ISREG(info.st_mode):
                entries.append(child)
            else:
                raise MaterialIntegrityError(
                    "NON_REGULAR_ENTRY", "L'inventario contiene un elemento non regolare."
                )
            if len(entries) > MAX_INVENTORY_ENTRIES:
                raise MaterialIntegrityError(
                    "INVENTORY_LIMIT_EXCEEDED",
                    "Numero massimo di elementi nell'inventario superato."
                )
        pending.extend(reversed(subdirectories))
    return sorted(entries, key=lambda item: item.relative_to(path).as_posix())


def _relative_source(item: Path, root: Path) -> str:
    relative = item.relative_to(root).as_posix()
    if not relative.startswith("intake/"):
        raise MaterialIntegrityError(
            "INVALID_ORIGINAL_PATH",
            "Il percorso di un file preparato non rimane sotto intake/.",
        )
    return relative



def _file_identity(info) -> tuple[int, int]:
    """Restituisce un'identità stabile oppure interrompe la lettura in sicurezza."""
    device = getattr(info, "st_dev", None)
    inode = getattr(info, "st_ino", None)
    if not isinstance(device, int) or not isinstance(inode, int) or inode <= 0:
        raise OSError("Il file system non fornisce un'identità stabile del file.")
    return device, inode


def _read_bounded_file(path: Path, expected_size: int) -> bytes:
    """Legge al massimo MAX_FILE_BYTES + 1 byte da un file regolare stabile.

    Il descrittore resta aperto durante la lettura. Il confronto tra identità
    osservata con lstat e fstat impedisce di leggere un collegamento simbolico
    sostituito tra il controllo del percorso e l'apertura.
    """
    before = path.lstat()
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise OSError("Il percorso non identifica un file regolare stabile.")

    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise OSError("Il descrittore non identifica un file regolare.")
        if _file_identity(opened) != _file_identity(before):
            raise OSError("Il file è cambiato durante l'apertura.")

        chunks = []
        remaining = MAX_FILE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)

        after_fd = os.fstat(descriptor)
        after_path = path.lstat()
        if not stat.S_ISREG(after_path.st_mode):
            raise OSError("Il percorso non identifica più un file regolare.")
        if _file_identity(after_fd) != _file_identity(opened):
            raise OSError("Il file aperto è cambiato durante la lettura.")
        if _file_identity(after_path) != _file_identity(opened):
            raise OSError("Il percorso è stato sostituito durante la lettura.")
        if len(raw) > MAX_FILE_BYTES or len(raw) != expected_size:
            raise OSError("La dimensione del file è cambiata o supera il limite.")
        if after_fd.st_size != expected_size:
            raise OSError("La dimensione del file è cambiata durante la lettura.")
        return raw
    finally:
        os.close(descriptor)

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
        return _failed_result(result, "failed", [_problem("MATERIAL_LOOKUP_FAILED", "Impossibile recuperare il record del materiale dal catalogo.")])

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
        digest=(
            integrity.get("actual_digest")
            if not is_remote and integrity.get("status") == "verified"
            else None
        ),
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
        selected_sizes: dict[Path, int] = {}
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

            try:
                size = item.stat().st_size
            except OSError:
                skipped.append({"source": source, "reason": "read_error"})
                continue
            if size > MAX_FILE_BYTES:
                skipped.append({"source": source, "reason": "file_too_large"})
            elif len(selected) >= MAX_FILES:
                skipped.append({"source": source, "reason": "max_files_reached"})
            elif selected_bytes + size > MAX_TOTAL_BYTES:
                skipped.append({"source": source, "reason": "total_size_limit"})
            else:
                selected.append(item)
                selected_sizes[item] = size
                selected_bytes += size

        prepared = []
        for item in selected:
            source = _relative_source(item, root)
            try:
                raw = _read_bounded_file(item, selected_sizes[item])
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
            [_problem("INVENTORY_FAILED", "Impossibile completare l'inventario del materiale a causa di un errore del file system.")],
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
