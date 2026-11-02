#!/usr/bin/env python3
"""Componente indipendente per acquisire e conservare materiali senza eseguirli."""
from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
import re
import shutil
import socket
import sys
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
MATERIAL_SCHEMA = "schemas/material-record.schema.json"
LOCK_NAME = ".materials-acquisition.lock"


class DuplicateMaterialError(ValueError):
    def __init__(self, existing_ids):
        self.existing_ids = tuple(sorted(set(existing_ids)))
        super().__init__("Contenuto già acquisito con identificativo/i: " + ", ".join(self.existing_ids))


def _timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_id(material_id):
    if not isinstance(material_id, str) or not ID_PATTERN.fullmatch(material_id):
        raise ValueError("Identificativo non valido: usare lettere minuscole, numeri, punti o trattini.")


def _reject_symlinks(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError(f"Collegamento simbolico non ammesso: {path}")
    if path.is_dir():
        for item in path.rglob("*"):
            if item.is_symlink():
                raise ValueError(f"Collegamento simbolico non ammesso: {item}")


def _digest_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest_directory(path):
    digest = hashlib.sha256()
    for item in sorted(Path(path).rglob("*"), key=lambda entry: entry.relative_to(path).as_posix()):
        if item.is_symlink():
            raise ValueError(f"Collegamento simbolico non ammesso: {item}")
        relative = item.relative_to(path).as_posix().encode("utf-8")
        if item.is_dir():
            digest.update(b"D\0" + relative + b"\0")
        elif item.is_file():
            digest.update(b"F\0" + relative + b"\0")
            with item.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            digest.update(b"\0")
    return digest.hexdigest()


def _digest_directory_legacy(path):
    digest = hashlib.sha256()
    for item in sorted(Path(path).rglob("*")):
        if item.is_symlink():
            raise ValueError(f"Collegamento simbolico non ammesso: {item}")
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\\0")
            with item.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            digest.update(b"\\0")
    return digest.hexdigest()


def _directory_size(path):
    return sum(item.stat().st_size for item in Path(path).rglob("*") if item.is_file())


def _infer_kind(source):
    if source.is_dir():
        return "directory"
    if zipfile.is_zipfile(source) or tarfile.is_tarfile(source):
        return "archive"
    return "file"


def _load_catalog(root):
    catalog_path = root / "catalog/materials.json"
    if not catalog_path.is_file():
        raise FileNotFoundError(f"Catalogo materiali non trovato: {catalog_path}")
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Catalogo materiali non leggibile: {exc}") from exc
    if not isinstance(catalog, dict) or catalog.get("catalog_version") != "1.0" or not isinstance(catalog.get("materials"), list):
        raise ValueError("Struttura del catalogo materiali non valida.")
    return catalog, catalog_path


def _validate_record(root, record):
    schema = json.loads((root / MATERIAL_SCHEMA).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(record), key=lambda error: list(error.absolute_path))
    if errors:
        raise ValueError("Scheda materiale non valida: " + "; ".join(error.message for error in errors))


def _append_record(root, record):
    catalog, catalog_path = _load_catalog(root)
    if any(isinstance(item, dict) and item.get("id") == record["id"] for item in catalog["materials"]):
        raise ValueError(f"Identificativo già presente nel catalogo: {record['id']}")
    _validate_record(root, record)
    catalog["materials"].append(record)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=catalog_path.parent, prefix=".materials-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(catalog, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, catalog_path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _base_record(material_id, name, description, method, source_label, status, original):
    record = {
        "id": material_id,
        "acquisition": {"status": status, "acquired_at": _timestamp(), "method": method, "original": original},
        "classification": {"status": "not_examined", "kind": "unclassified"},
        "documentation": {"status": "unknown"},
        "verification": {"status": "not_verified"},
        "usability": {"status": "not_assessed"}
    }
    if name:
        record["name"] = name
    if description is not None:
        record["description"] = description
    if source_label:
        record["acquisition"]["source"] = source_label
    return record


def _pid_is_alive(pid):
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel.OpenProcess(0x00100000, False, pid)  # SYNCHRONIZE
        if handle:
            kernel.CloseHandle(handle)
            return True
        return ctypes.get_last_error() != 87  # ERROR_INVALID_PARAMETER means no such PID
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as exc:
        return exc.errno != errno.ESRCH


def _acquisition_lock(root):
    lock_path = Path(root) / LOCK_NAME
    for _ in range(3):
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            try:
                lock = json.loads(lock_path.read_text(encoding="utf-8"))
                pid, host = lock["pid"], lock["hostname"]
                if not isinstance(pid, int) or pid <= 0 or not isinstance(host, str):
                    raise ValueError("campi pid/hostname non validi")
            except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise RuntimeError("Blocco di acquisizione illeggibile: intervento manuale necessario.") from exc
            if host != socket.gethostname():
                raise RuntimeError("Blocco creato da un altro computer: impossibile stabilire se sia inattivo.")
            if _pid_is_alive(pid):
                raise RuntimeError("È già in corso un'altra acquisizione.")
            lock_path.unlink(missing_ok=True)
        else:
            try:
                os.write(descriptor, json.dumps({
                    "pid": os.getpid(), "hostname": socket.gethostname(), "created_at": _timestamp()
                }).encode("utf-8"))
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            return lock_path
    raise RuntimeError("Impossibile acquisire il blocco esclusivo; riprovare.")


def _safe_intake_child(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or len(Path(name).parts) != 1 or name in {".", ".."}:
        raise ValueError("Percorso di transazione non sicuro.")
    child = root / "intake" / name
    if child.is_symlink():
        raise ValueError("La transazione contiene un collegamento simbolico.")
    return child


def _record_original_path(root, record):
    relative = record["acquisition"]["original"].get("path")
    pure = PurePosixPath(relative) if isinstance(relative, str) else None
    if pure is None or pure.is_absolute() or not pure.parts or pure.parts[0] != "intake" or ".." in pure.parts:
        raise ValueError("Percorso dell'originale nella transazione non valido.")
    candidate = root.joinpath(*pure.parts)
    current = candidate
    while current != root:
        if current.is_symlink():
            raise ValueError("Collegamento simbolico nell'originale della transazione.")
        current = current.parent
    resolved = candidate.resolve()
    try:
        resolved.relative_to((root / "intake").resolve())
    except ValueError as exc:
        raise ValueError("Originale della transazione fuori da intake/.") from exc
    return resolved


def _verify_record_content(root, record):
    original = record["acquisition"]["original"]
    path = _record_original_path(root, record)
    if not path.exists():
        raise RuntimeError(f"Originale mancante durante il recupero: {path}")
    algorithm = original.get("digest_algorithm")
    if path.is_dir():
        actual = _digest_directory_legacy(path) if algorithm is None else _digest_directory(path)
        if algorithm not in {None, "sha256-tree-v2"}:
            raise RuntimeError(f"Algoritmo impronta non supportato: {algorithm}")
    else:
        actual = _digest_file(path)
        if algorithm not in {None, "sha256-file-v1"}:
            raise RuntimeError(f"Algoritmo impronta non supportato: {algorithm}")
    if actual != original.get("sha256"):
        raise RuntimeError(f"Impronta non corrispondente durante il recupero: {record['id']}")
    return path


def _recover_transactions_locked(root):
    intake = root / "intake"
    intake.mkdir(parents=True, exist_ok=True)
    transactions = intake / ".transactions"
    completed, discarded, registered = [], [], []
    if transactions.exists():
        if transactions.is_symlink() or not transactions.is_dir():
            raise RuntimeError("Cartella delle transazioni non sicura.")
        for journal_path in sorted(transactions.glob("*.json")):
            if journal_path.is_symlink():
                raise RuntimeError(f"Registro di transazione non sicuro: {journal_path}")
            try:
                journal = json.loads(journal_path.read_text(encoding="utf-8"))
                if journal.get("version") != 1 or not isinstance(journal.get("id"), str) or not isinstance(journal.get("record"), dict):
                    raise ValueError("formato del registro non riconosciuto")
                material_id, record = journal["id"], journal["record"]
                if record.get("id") != material_id:
                    raise ValueError("identificativo del registro e della scheda non coincidono")
                destination = _safe_intake_child(root, journal.get("destination"))
                stage = _safe_intake_child(root, journal["stage"]) if journal.get("stage") else None
                catalog, _ = _load_catalog(root)
                existing = next((item for item in catalog["materials"] if isinstance(item, dict) and item.get("id") == material_id), None)
                if existing is not None:
                    old_original = existing.get("acquisition", {}).get("original", {})
                    new_original = record.get("acquisition", {}).get("original", {})
                    if old_original.get("sha256") != new_original.get("sha256") or old_original.get("path") != new_original.get("path"):
                        raise RuntimeError("il catalogo contiene già un identificativo collegato a un contenuto diverso")
                    _verify_record_content(root, existing)
                    if stage and stage.exists():
                        shutil.rmtree(stage)
                    registered.append(material_id)
                elif destination.exists():
                    if stage and stage.exists():
                        raise RuntimeError("coesistono copia temporanea e destinazione definitiva")
                    _verify_record_content(root, record)
                    _append_record(root, record)
                    completed.append(material_id)
                elif stage and stage.exists():
                    shutil.rmtree(stage)
                    discarded.append(material_id)
                else:
                    discarded.append(material_id)
                journal_path.unlink()
            except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError, RuntimeError) as exc:
                raise RuntimeError(f"Recupero interrotto per {journal_path.name}: {exc}") from exc

    for child in sorted(intake.iterdir()):
        if child.is_dir() and child.name.startswith(".staging-"):
            if child.is_symlink():
                raise RuntimeError(f"Cartella temporanea non sicura: {child}")
            shutil.rmtree(child)
            discarded.append(child.name)
    if transactions.exists() and not any(transactions.iterdir()):
        transactions.rmdir()
    return {"completed": completed, "discarded_staging": discarded, "already_registered": registered}


def recover_interrupted_acquisitions(root):
    """Recupera transazioni lasciate da un arresto anomalo senza sovrascrivere dati."""
    root = Path(root).resolve()
    lock_path = _acquisition_lock(root)
    try:
        return _recover_transactions_locked(root)
    finally:
        lock_path.unlink(missing_ok=True)


def _find_duplicate_ids(root, digest, source_is_directory, legacy_digest=None):
    catalog, _ = _load_catalog(root)
    matches = []
    for item in catalog["materials"]:
        if not isinstance(item, dict):
            continue
        acquisition = item.get("acquisition", {})
        original = acquisition.get("original", {}) if isinstance(acquisition, dict) else {}
        accepted_digests = {digest, legacy_digest}
        if acquisition.get("status") != "preserved" or original.get("sha256") not in accepted_digests or not original.get("path"):
            continue
        try:
            existing_path = _record_original_path(root, item)
        except (OSError, ValueError, KeyError, TypeError):
            continue
        if existing_path.exists() and existing_path.is_dir() == source_is_directory:
            matches.append(item["id"])
    return matches


def acquire_material(root, source, material_id, *, name=None, description=None,
                     method="local_copy", source_label=None, kind=None):
    """Copia un file o una cartella nella libreria e registra la scheda descrittiva."""
    _validate_id(material_id)
    root = Path(root).resolve()
    source_input = Path(source).expanduser()
    if not source_input.exists():
        raise FileNotFoundError(f"Materiale sorgente non trovato: {source_input}")
    if source_input.is_symlink():
        raise ValueError("Il materiale sorgente non può essere un collegamento simbolico.")
    source_path = source_input.resolve(strict=True)
    _reject_symlinks(source_path)
    if not (source_path.is_file() or source_path.is_dir()):
        raise ValueError("Sono ammessi soltanto file e cartelle.")
    try:
        source_path.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("La sorgente non può trovarsi all'interno della libreria stessa.")

    inferred = _infer_kind(source_path)
    material_kind = kind or inferred
    if material_kind not in {"file", "directory", "archive", "package", "unknown"}:
        raise ValueError(f"Tipo di materiale non supportato: {material_kind}")
    if source_path.is_dir() and material_kind not in {"directory", "package", "unknown"}:
        raise ValueError("Una cartella può essere registrata come directory, package o unknown.")
    if source_path.is_file() and material_kind == "directory":
        raise ValueError("Un file non può essere registrato come directory.")
    if source_path.is_file() and inferred == "archive" and kind is None:
        material_kind = "archive"

    intake = root / "intake"
    intake.mkdir(parents=True, exist_ok=True)
    folder_name = material_id.replace(".", "-")
    destination = intake / folder_name
    lock_path = _acquisition_lock(root)
    stage = None
    journal_path = None
    try:
        _recover_transactions_locked(root)
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"La destinazione esiste già e non verrà sovrascritta: {destination}")
        catalog, _ = _load_catalog(root)
        if any(isinstance(item, dict) and item.get("id") == material_id for item in catalog["materials"]):
            raise ValueError(f"Identificativo già presente nel catalogo: {material_id}")

        stage = Path(tempfile.mkdtemp(prefix=f".staging-{folder_name}-", dir=intake))
        staged_source = stage / "source"
        if source_path.is_dir():
            shutil.copytree(source_path, staged_source, copy_function=shutil.copy2)
            digest, byte_size = _digest_directory(staged_source), _directory_size(staged_source)
            stored_path = f"intake/{folder_name}/source"
        else:
            staged_source.mkdir()
            copied_file = staged_source / source_path.name
            shutil.copy2(source_path, copied_file)
            digest, byte_size = _digest_file(copied_file), copied_file.stat().st_size
            stored_path = f"intake/{folder_name}/source/{source_path.name}"

        source_digest = _digest_directory(source_path) if source_path.is_dir() else _digest_file(source_path)
        if source_digest != digest:
            raise OSError("La copia acquisita non coincide con il materiale sorgente.")
        legacy_digest = _digest_directory_legacy(source_path) if source_path.is_dir() else None
        duplicates = _find_duplicate_ids(root, digest, source_path.is_dir(), legacy_digest)
        if duplicates:
            raise DuplicateMaterialError(duplicates)

        record = _base_record(material_id, name or source_path.name, description, method, source_label,
            "preserved", {"kind": material_kind, "path": stored_path, "sha256": digest,
                "digest_algorithm": "sha256-tree-v2" if source_path.is_dir() else "sha256-file-v1",
                "byte_size": byte_size})
        _validate_record(root, record)

        transactions = intake / ".transactions"
        transactions.mkdir(parents=True, exist_ok=True)
        journal_path = transactions / f"{folder_name}.json"
        if journal_path.exists():
            raise RuntimeError(f"Esiste già una transazione non risolta per {material_id}.")
        journal = {"version": 1, "id": material_id, "stage": stage.name, "destination": destination.name, "record": record}
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=transactions, prefix=".journal-", suffix=".tmp", delete=False) as stream:
            temporary_journal = Path(stream.name)
            json.dump(journal, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_journal, journal_path)

        os.rename(stage, destination)
        stage = None
        try:
            _append_record(root, record)
        except Exception:
            shutil.rmtree(destination, ignore_errors=True)
            journal_path.unlink(missing_ok=True)
            raise
        journal_path.unlink(missing_ok=True)
        if transactions.exists() and not any(transactions.iterdir()):
            transactions.rmdir()
        return record
    finally:
        if stage is not None:
            shutil.rmtree(stage, ignore_errors=True)
        lock_path.unlink(missing_ok=True)


def acquire_remote_material(root, material_id, uri, *, name=None, description=None,
                            method="remote_reference", source_label=None):
    """Registra un riferimento remoto senza dichiarare di averne una copia locale."""
    _validate_id(material_id)
    parsed = urlparse(uri) if isinstance(uri, str) else None
    if parsed is None or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Il riferimento remoto deve essere un URI HTTP o HTTPS valido.")
    root = Path(root).resolve()
    record = _base_record(material_id, name, description, method, source_label, "received",
        {"kind": "remote_reference", "uri": uri})
    lock_path = _acquisition_lock(root)
    try:
        _recover_transactions_locked(root)
        catalog, _ = _load_catalog(root)
        if any(isinstance(item, dict) and item.get("id") == material_id for item in catalog["materials"]):
            raise ValueError(f"Identificativo già presente nel catalogo: {material_id}")
        duplicates = [item["id"] for item in catalog["materials"] if isinstance(item, dict)
            and item.get("acquisition", {}).get("original", {}).get("kind") == "remote_reference"
            and item.get("acquisition", {}).get("original", {}).get("uri") == uri]
        if duplicates:
            raise DuplicateMaterialError(duplicates)
        _append_record(root, record)
        return record
    finally:
        lock_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Acquisisce un materiale senza eseguirlo o modificarlo.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--id", required=True, dest="material_id")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--uri")
    parser.add_argument("--name")
    parser.add_argument("--description")
    parser.add_argument("--method", default=None)
    parser.add_argument("--source-label")
    parser.add_argument("--kind", choices=["file", "directory", "archive", "package", "unknown"])
    args = parser.parse_args()
    if bool(args.source) == bool(args.uri):
        parser.error("Specificare uno e un solo elemento tra --source e --uri.")
    try:
        if args.uri:
            record = acquire_remote_material(args.root, args.material_id, args.uri, name=args.name,
                description=args.description, method=args.method or "remote_reference", source_label=args.source_label)
        else:
            record = acquire_material(args.root, args.source, args.material_id, name=args.name,
                description=args.description, method=args.method or "local_copy", source_label=args.source_label, kind=args.kind)
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ACQUISIZIONE FALLITA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
