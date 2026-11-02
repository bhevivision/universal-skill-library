#!/usr/bin/env python3
"""Servizio comune per identità, percorsi e integrità dei materiali acquisiti.

Il modulo non esegue, interpreta, estrae o modifica i materiali. I riferimenti
remoti vengono controllati solo come metadati: il contenuto non viene visitato.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse


SCHEMA_VERSION = "1.0"
DEFAULT_ALLOWED_STATES = ("preserved",)
CHUNK_SIZE = 1024 * 1024


class MaterialIntegrityError(ValueError):
    """Errore strutturale con codice stabile e adatto alla gestione automatica."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def _problem(code: str, message: str) -> dict:
    return {"code": code, "message": message}


def _check(name: str, status: str, detail: str) -> dict:
    return {"name": name, "status": status, "detail": detail}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_tree(path: Path, *, legacy: bool = False) -> str:
    """Replica sha256-tree-v2 e la precedente impronta directory senza versione."""
    digest = hashlib.sha256()
    entries = sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix())
    for item in entries:
        if item.is_symlink():
            raise MaterialIntegrityError(
                "SYMLINK_NOT_ALLOWED",
                f"Collegamento simbolico non ammesso nel materiale: {item}",
            )
        relative = item.relative_to(path).as_posix().encode("utf-8")
        if item.is_dir() and not legacy:
            digest.update(b"D\0" + relative + b"\0")
        elif item.is_file():
            if legacy:
                digest.update(relative + b"\0")
            else:
                digest.update(b"F\0" + relative + b"\0")
            with item.open("rb") as stream:
                for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
                    digest.update(chunk)
            digest.update(b"\0")
    return digest.hexdigest()


def _safe_catalog_path(root: Path) -> Path:
    catalog_dir = root / "catalog"
    catalog_path = catalog_dir / "materials.json"
    if catalog_dir.is_symlink() or catalog_path.is_symlink():
        raise MaterialIntegrityError(
            "SYMLINK_NOT_ALLOWED", "Il percorso del catalogo contiene un collegamento simbolico."
        )
    if not catalog_path.is_file():
        raise MaterialIntegrityError(
            "CATALOG_UNREADABLE", "Il catalogo catalog/materials.json non esiste o non è un file regolare."
        )
    try:
        resolved = catalog_path.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise MaterialIntegrityError(
            "CATALOG_UNREADABLE", "Il catalogo non è contenuto nella cartella della libreria."
        ) from exc
    return resolved


def _read_catalog(root: Path) -> tuple[dict, Path, str]:
    catalog_path = _safe_catalog_path(root)
    try:
        raw = catalog_path.read_bytes()
        catalog = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MaterialIntegrityError(
            "CATALOG_UNREADABLE", f"Il catalogo materiali non è leggibile: {exc}"
        ) from exc
    if (
        not isinstance(catalog, dict)
        or catalog.get("catalog_version") != "1.0"
        or not isinstance(catalog.get("materials"), list)
    ):
        raise MaterialIntegrityError(
            "CATALOG_INVALID", "Struttura del catalogo materiali non valida."
        )
    return catalog, catalog_path, hashlib.sha256(raw).hexdigest()


def _load_material_record(root: Path, material_id: str):
    if not isinstance(material_id, str) or not material_id:
        raise MaterialIntegrityError("INVALID_RECORD", "Identificativo del materiale mancante o non valido.")
    catalog, catalog_path, catalog_digest = _read_catalog(root)
    matches = [
        item for item in catalog["materials"]
        if isinstance(item, dict) and item.get("id") == material_id
    ]
    if len(matches) > 1:
        raise MaterialIntegrityError(
            "DUPLICATE_MATERIAL_ID", f"Identificativo duplicato nel catalogo: {material_id}"
        )
    if not matches:
        raise MaterialIntegrityError("MATERIAL_NOT_FOUND", f"Materiale non trovato: {material_id}")
    try:
        current_digest = _sha256_file(catalog_path)
    except OSError as exc:
        raise MaterialIntegrityError("IO_ERROR", f"Impossibile rileggere il catalogo: {exc}") from exc
    if current_digest != catalog_digest:
        raise MaterialIntegrityError(
            "CATALOG_CHANGED_DURING_CHECK", "Il catalogo è cambiato durante la lettura del record."
        )
    return matches[0], catalog, catalog_path, catalog_digest


def load_material_record(root, material_id: str):
    """Carica il record univoco e restituisce (record, catalogo, percorso_catalogo).

    Questa funzione controlla la struttura e l'identità nel catalogo, ma non
    calcola l'impronta del materiale originale.
    """
    record, catalog, catalog_path, _ = _load_material_record(Path(root).resolve(), material_id)
    return record, catalog, catalog_path


def _safe_original_path(root: Path, original: dict) -> Path:
    relative_value = original.get("path")
    if (
        not isinstance(relative_value, str)
        or not relative_value
        or "\\" in relative_value
        or "\x00" in relative_value
    ):
        raise MaterialIntegrityError("INVALID_ORIGINAL_PATH", "Percorso dell'originale non valido.")
    pieces = relative_value.split("/")
    pure = PurePosixPath(relative_value)
    if (
        pure.is_absolute()
        or not pure.parts
        or pure.parts[0] != "intake"
        or any(part in {"", ".", ".."} or ":" in part for part in pieces)
    ):
        raise MaterialIntegrityError(
            "INVALID_ORIGINAL_PATH", "Il percorso dell'originale deve essere relativo e rimanere in intake/."
        )

    intake_root = root / "intake"
    if intake_root.is_symlink():
        raise MaterialIntegrityError("SYMLINK_NOT_ALLOWED", "La cartella intake non può essere un collegamento simbolico.")
    candidate = root.joinpath(*pure.parts)
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            raise MaterialIntegrityError(
                "SYMLINK_NOT_ALLOWED", f"Collegamento simbolico nel percorso dell'originale: {relative_value}"
            )
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(intake_root.resolve(strict=True))
    except FileNotFoundError as exc:
        raise MaterialIntegrityError(
            "ORIGINAL_NOT_FOUND", f"Originale non disponibile: {relative_value}"
        ) from exc
    except (OSError, RuntimeError, ValueError) as exc:
        raise MaterialIntegrityError(
            "PATH_OUTSIDE_INTAKE", f"Originale fuori dalla cartella intake: {relative_value}"
        ) from exc
    if not (resolved.is_file() or resolved.is_dir()):
        raise MaterialIntegrityError(
            "ORIGINAL_NOT_FOUND", f"L'originale non è un file o una cartella regolare: {relative_value}"
        )
    return resolved


def _digest_original(path: Path, original: dict) -> tuple[str, str]:
    algorithm = original.get("digest_algorithm")
    if path.is_dir():
        if algorithm not in {None, "sha256-tree-v2"}:
            raise MaterialIntegrityError(
                "UNSUPPORTED_DIGEST_ALGORITHM",
                f"Algoritmo di impronta non valido per una cartella: {algorithm}",
            )
        return _sha256_tree(path, legacy=algorithm is None), (
            "sha256-tree-legacy" if algorithm is None else "sha256-tree-v2"
        )
    if algorithm not in {None, "sha256-file-v1"}:
        raise MaterialIntegrityError(
            "UNSUPPORTED_DIGEST_ALGORITHM",
            f"Algoritmo di impronta non valido per un file: {algorithm}",
        )
    return _sha256_file(path), "sha256-file-v1"


def _result_base(material_id, kind=None, state=None, path=None, recorded=None):
    return {
        "schema_version": SCHEMA_VERSION,
        "material_id": material_id,
        "original_kind": kind,
        "acquisition_state": state,
        "path": path,
        "recorded_digest": recorded,
        "actual_digest": None,
        "digest_algorithm": None,
        "status": "failed",
        "checks": [],
        "problems": [],
    }


def verify_material(
    root,
    material_id: str,
    expected_digest: str | None = None,
    allowed_states=DEFAULT_ALLOWED_STATES,
) -> dict:
    """Verifica record, stato, percorso e impronta; non modifica alcun dato.

    Stati del risultato:
    - verified: materiale locale e impronta controllati;
    - not_applicable: riferimento remoto, contenuto non visitato;
    - blocked: condizione di sicurezza, stato o integrità non accettabile;
    - failed: errore tecnico o strutturale che impedisce il controllo.
    """
    root = Path(root).resolve()
    result = _result_base(material_id)
    if isinstance(allowed_states, str) or not isinstance(allowed_states, (list, tuple, set, frozenset)) or not all(
        isinstance(state, str) for state in allowed_states
    ):
        result["problems"].append(_problem("INVALID_RECORD", "Elenco degli stati di acquisizione ammessi non valido."))
        result["status"] = "failed"
        return result
    catalog_path = None
    initial_catalog_digest = None
    original = None
    material_path = None

    try:
        record, catalog, catalog_path, initial_catalog_digest = _load_material_record(root, material_id)
        acquisition = record.get("acquisition")
        if not isinstance(acquisition, dict):
            raise MaterialIntegrityError("INVALID_RECORD", "Sezione acquisition assente o non valida.")
        original = acquisition.get("original")
        if not isinstance(original, dict):
            raise MaterialIntegrityError("INVALID_RECORD", "Sezione acquisition.original assente o non valida.")
        kind = original.get("kind")
        state = acquisition.get("status")
        recorded_digest = original.get("sha256")
        if kind not in {"file", "directory", "archive", "package", "remote_reference", "unknown"}:
            raise MaterialIntegrityError("INVALID_RECORD", f"Tipo originale assente o non riconosciuto: {kind}")
        result.update({
            "original_kind": kind,
            "acquisition_state": state,
            "recorded_digest": recorded_digest,
        })
        result["checks"].append(_check("catalog_identity", "passed", "Record univoco trovato nel catalogo."))

        if kind == "remote_reference":
            uri = original.get("uri")
            parsed = urlparse(uri) if isinstance(uri, str) else None
            if not parsed or parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
                raise MaterialIntegrityError("INVALID_RECORD", "URI del riferimento remoto assente o non valida.")
            if state not in {"received", "preserved"}:
                raise MaterialIntegrityError(
                    "INVALID_ACQUISITION_STATE", f"Stato non valido per il riferimento remoto: {state}"
                )
            result["status"] = "not_applicable"
            result["checks"].append(_check("remote_reference", "passed", "URI e stato del riferimento controllati; contenuto non visitato."))
            result["problems"].append(_problem(
                "REMOTE_CONTENT_NOT_CHECKED",
                "Il contenuto remoto non è stato visitato né scaricato; non è stata verificata alcuna impronta del contenuto.",
            ))
            if _sha256_file(catalog_path) != initial_catalog_digest:
                raise MaterialIntegrityError(
                    "CATALOG_CHANGED_DURING_CHECK", "Il catalogo è cambiato durante la verifica."
                )
            return result

        if state not in allowed_states:
            raise MaterialIntegrityError(
                "INVALID_ACQUISITION_STATE",
                f"Stato di acquisizione non consentito: {state}. Stati ammessi: {', '.join(allowed_states)}.",
            )
        if not isinstance(recorded_digest, str) or len(recorded_digest) != 64 or any(char not in "0123456789abcdef" for char in recorded_digest):
            raise MaterialIntegrityError("INVALID_RECORD", "Impronta SHA-256 registrata assente o non valida.")
        material_path = _safe_original_path(root, original)
        result["path"] = material_path.relative_to(root).as_posix()
        result["checks"].append(_check("safe_path", "passed", "Percorso relativo, contenuto in intake/ e privo di collegamenti simbolici."))

        if kind == "directory" and not material_path.is_dir():
            raise MaterialIntegrityError("INVALID_RECORD", "Il tipo originale directory non corrisponde a una cartella.")
        if kind in {"file", "archive"} and not material_path.is_file():
            raise MaterialIntegrityError("INVALID_RECORD", f"Il tipo originale {kind} non corrisponde a un file.")

        actual_digest, algorithm = _digest_original(material_path, original)
        result["actual_digest"] = actual_digest
        result["digest_algorithm"] = algorithm
        result["checks"].append(_check("content_fingerprint", "passed" if actual_digest == recorded_digest else "failed", "Impronta SHA-256 ricalcolata sul contenuto originale."))
        if actual_digest != recorded_digest:
            raise MaterialIntegrityError(
                "DIGEST_MISMATCH", "L'impronta del materiale non corrisponde a quella registrata all'acquisizione."
            )
        if expected_digest is not None:
            if not isinstance(expected_digest, str) or len(expected_digest) != 64 or expected_digest != recorded_digest or expected_digest != actual_digest:
                raise MaterialIntegrityError(
                    "EXPECTED_DIGEST_MISMATCH", "L'impronta attesa non coincide con catalogo e contenuto effettivo."
                )
            result["checks"].append(_check("expected_fingerprint", "passed", "Impronta attesa coerente con catalogo e contenuto."))

        if _sha256_file(catalog_path) != initial_catalog_digest:
            raise MaterialIntegrityError(
                "CATALOG_CHANGED_DURING_CHECK", "Il catalogo è cambiato durante la verifica."
            )
        # Seconda impronta per rilevare modifiche avvenute durante il controllo.
        final_digest, _ = _digest_original(material_path, original)
        if final_digest != actual_digest:
            raise MaterialIntegrityError(
                "DIGEST_CHANGED_DURING_CHECK", "Il materiale è cambiato durante la verifica."
            )
        result["checks"].append(_check("final_recheck", "passed", "Catalogo e impronta del materiale ricontrollati al termine."))
        result["status"] = "verified"
        return result

    except MaterialIntegrityError as exc:
        result["problems"].append(_problem(exc.code, str(exc)))
        result["status"] = "blocked" if exc.code in {
            "MATERIAL_NOT_FOUND", "DUPLICATE_MATERIAL_ID", "INVALID_RECORD",
            "INVALID_ACQUISITION_STATE", "INVALID_ORIGINAL_PATH", "PATH_OUTSIDE_INTAKE",
            "SYMLINK_NOT_ALLOWED", "ORIGINAL_NOT_FOUND", "DIGEST_MISMATCH",
            "EXPECTED_DIGEST_MISMATCH", "CATALOG_CHANGED_DURING_CHECK",
            "DIGEST_CHANGED_DURING_CHECK",
        } else "failed"
        return result
    except (OSError, UnicodeError, RuntimeError) as exc:
        result["problems"].append(_problem("IO_ERROR", f"Errore durante il controllo: {exc}"))
        result["status"] = "failed"
        return result


__all__ = [
    "MaterialIntegrityError",
    "load_material_record",
    "verify_material",
]
