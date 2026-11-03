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
import stat
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
MAX_ACQUISITION_FILES = 10000
MAX_ACQUISITION_BYTES = 1073741824
MAX_ACQUISITION_DEPTH = 64
MAX_ACQUISITION_ENTRIES = 10000


class DuplicateMaterialError(ValueError):
    def __init__(self, existing_ids):
        self.existing_ids = tuple(sorted(set(existing_ids)))
        super().__init__("Contenuto già acquisito con identificativo/i: " + ", ".join(self.existing_ids))


def _timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_id(material_id):
    if not isinstance(material_id, str) or not ID_PATTERN.fullmatch(material_id):
        raise ValueError("Identificativo non valido: usare lettere minuscole, numeri, punti o trattini.")


def _is_reparse_point(info):
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(info, "st_file_attributes", 0) & flag)


def _bounded_entries(path):
    """Elenca un albero entro limiti rigidi di elementi e profondità."""
    path = Path(path)
    root_info = path.lstat()
    if stat.S_ISLNK(root_info.st_mode) or _is_reparse_point(root_info):
        raise ValueError(f"Collegamento o punto di reindirizzamento non ammesso: {path}")
    if stat.S_ISREG(root_info.st_mode):
        info = root_info
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"Elemento non regolare non ammesso: {path}")
        return [(path, "file", info)]
    if not path.is_dir():
        raise ValueError(f"Sorgente non regolare non ammessa: {path}")

    entries = []
    pending = [(path, 0)]
    file_count = 0
    total_bytes = 0
    while pending:
        current, depth = pending.pop()
        children = []
        with os.scandir(current) as iterator:
            for entry in iterator:
                children.append(entry)
                if len(entries) + len(children) > MAX_ACQUISITION_ENTRIES:
                    raise ValueError("Il materiale supera il numero massimo di elementi acquisibili.")
        children.sort(key=lambda item: item.name)
        subdirectories = []
        for entry in children:
            child = Path(entry.path)
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode) or _is_reparse_point(info):
                raise ValueError(f"Collegamento o punto di reindirizzamento non ammesso: {child}")
            if stat.S_ISDIR(info.st_mode):
                if depth + 1 > MAX_ACQUISITION_DEPTH:
                    raise ValueError("Il materiale supera la profondità massima consentita.")
                entries.append((child, "directory", info))
                subdirectories.append((child, depth + 1))
            elif stat.S_ISREG(info.st_mode):
                file_count += 1
                total_bytes += info.st_size
                if file_count > MAX_ACQUISITION_FILES:
                    raise ValueError("Il materiale supera il numero massimo di file acquisibili.")
                if total_bytes > MAX_ACQUISITION_BYTES:
                    raise ValueError("Il materiale supera il limite massimo di byte acquisibili.")
                entries.append((child, "file", info))
            else:
                raise ValueError(f"Elemento non regolare non ammesso: {child}")
            if len(entries) > MAX_ACQUISITION_ENTRIES:
                raise ValueError("Il materiale supera il numero massimo di elementi acquisibili.")
        pending.extend(reversed(subdirectories))
    return sorted(entries, key=lambda item: item[0].relative_to(path).as_posix())


def _inspect_source(path):
    """Controlla la sorgente senza seguire collegamenti e con risorse limitate."""
    entries = _bounded_entries(Path(path))
    files = [item for item in entries if item[1] == "file"]
    total_bytes = sum(item[2].st_size for item in files)
    if len(files) > MAX_ACQUISITION_FILES:
        raise ValueError("Il materiale supera il numero massimo di file acquisibili.")
    if total_bytes > MAX_ACQUISITION_BYTES:
        raise ValueError("Il materiale supera il limite massimo di byte acquisibili.")
    return len(files), total_bytes


def _copy_file_bounded(source, destination, counters):
    """Copia un file regolare limitando i byte effettivamente letti, anche se cresce."""
    source = Path(source)
    destination = Path(destination)
    before = source.lstat()
    if stat.S_ISLNK(before.st_mode) or _is_reparse_point(before) or not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Elemento non regolare non ammesso: {source}")
    if counters["files"] + 1 > MAX_ACQUISITION_FILES:
        raise ValueError("Il materiale supera il numero massimo di file acquisibili.")
    remaining_budget = MAX_ACQUISITION_BYTES - counters["bytes"]
    if before.st_size > remaining_budget:
        raise ValueError("Il materiale supera il limite massimo di byte acquisibili.")

    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(source, flags)
    copied = 0
    try:
        opened = os.fstat(descriptor)
        identity = (before.st_dev, before.st_ino)
        if not stat.S_ISREG(opened.st_mode) or _is_reparse_point(opened) or (opened.st_dev, opened.st_ino) != identity:
            raise ValueError("Il file sorgente è cambiato durante l'apertura.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as output:
            while True:
                allowance = min(1024 * 1024, remaining_budget - copied + 1)
                chunk = os.read(descriptor, allowance)
                if not chunk:
                    break
                copied += len(chunk)
                if copied > remaining_budget:
                    raise ValueError("Il materiale supera il limite massimo di byte acquisibili durante la copia.")
                output.write(chunk)
            output.flush()
            os.fsync(output.fileno())
        after_fd = os.fstat(descriptor)
        after_path = source.lstat()
        if (after_fd.st_dev, after_fd.st_ino) != identity:
            raise ValueError("Il file sorgente è cambiato durante la copia.")
        if (after_path.st_dev, after_path.st_ino) != identity or stat.S_ISLNK(after_path.st_mode) or _is_reparse_point(after_path):
            raise ValueError("Il percorso sorgente è stato sostituito durante la copia.")
        if after_fd.st_size != copied or before.st_size != copied:
            raise ValueError("La dimensione del file sorgente è cambiata durante la copia.")
        os.chmod(destination, stat.S_IMODE(before.st_mode))
        os.utime(destination, ns=(before.st_atime_ns, before.st_mtime_ns))
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        os.close(descriptor)
    counters["files"] += 1
    counters["bytes"] += copied


def _copy_directory_bounded(source, destination):
    """Copia un albero con limiti applicati durante la lettura effettiva."""
    source = Path(source)
    destination = Path(destination)
    source_info = source.lstat()
    if stat.S_ISLNK(source_info.st_mode) or _is_reparse_point(source_info) or not stat.S_ISDIR(source_info.st_mode):
        raise ValueError("La cartella sorgente è cambiata o non è sicura.")
    entries = _bounded_entries(source)
    destination.mkdir(parents=True, exist_ok=False)
    for item, kind, info in sorted(
        (entry for entry in entries if entry[1] == "directory"),
        key=lambda entry: (len(entry[0].relative_to(source).parts), entry[0].relative_to(source).as_posix())
    ):
        target = destination / item.relative_to(source)
        target.mkdir(parents=True, exist_ok=True)
        os.chmod(target, stat.S_IMODE(info.st_mode))
    counters = {"files": 0, "bytes": 0}
    for item, kind, _info in entries:
        if kind == "file":
            _copy_file_bounded(item, destination / item.relative_to(source), counters)
    for item, kind, info in entries:
        if kind == "directory":
            after = item.lstat()
            if stat.S_ISLNK(after.st_mode) or (after.st_dev, after.st_ino) != (info.st_dev, info.st_ino):
                raise ValueError(f"La cartella sorgente è stata sostituita durante la copia: {item}")
    source_after = source.lstat()
    if stat.S_ISLNK(source_after.st_mode) or _is_reparse_point(source_after) or not stat.S_ISDIR(source_after.st_mode):
        raise ValueError("La cartella sorgente è stata sostituita durante la copia.")
    if os.name != "nt" and (source_after.st_dev, source_after.st_ino) != (source_info.st_dev, source_info.st_ino):
        raise ValueError("La cartella sorgente è stata sostituita durante la copia.")
    return counters["files"], counters["bytes"]


def _update_digest_from_file(digest, path):
    path = Path(path)
    before = path.lstat()
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Il percorso non identifica un file regolare: {path}")
    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        identity = (before.st_dev, before.st_ino)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != identity:
            raise ValueError(f"Il file è cambiato durante l'apertura: {path}")
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        after_fd = os.fstat(descriptor)
        after_path = path.lstat()
        if (after_fd.st_dev, after_fd.st_ino) != identity:
            raise ValueError(f"Il file è cambiato durante la lettura: {path}")
        if (after_path.st_dev, after_path.st_ino) != identity or stat.S_ISLNK(after_path.st_mode):
            raise ValueError(f"Il percorso è stato sostituito durante la lettura: {path}")
        if after_fd.st_size != opened.st_size:
            raise ValueError(f"La dimensione del file è cambiata durante la lettura: {path}")
    finally:
        os.close(descriptor)


def _digest_file(path):
    digest = hashlib.sha256()
    _update_digest_from_file(digest, path)
    return digest.hexdigest()


def _digest_directory(path):
    digest = hashlib.sha256()
    for item, kind, _info in _bounded_entries(Path(path)):
        relative = item.relative_to(path).as_posix().encode("utf-8")
        if kind == "directory":
            digest.update(b"D\0" + relative + b"\0")
        else:
            digest.update(b"F\0" + relative + b"\0")
            _update_digest_from_file(digest, item)
            digest.update(b"\0")
    return digest.hexdigest()


def _digest_directory_legacy(path):
    digest = hashlib.sha256()
    for item, kind, _info in _bounded_entries(Path(path)):
        if kind == "file":
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            _update_digest_from_file(digest, item)
            digest.update(b"\0")
    return digest.hexdigest()


def _directory_size(path):
    return sum(info.st_size for _item, kind, info in _bounded_entries(Path(path)) if kind == "file")


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
    if lock_path.is_symlink():
        raise RuntimeError("Il blocco di acquisizione non può essere un collegamento simbolico.")
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


def _ensure_intake(root):
    intake = Path(root) / "intake"
    if intake.is_symlink():
        raise ValueError("La cartella intake non può essere un collegamento simbolico.")
    intake.mkdir(parents=True, exist_ok=True)
    try:
        intake.resolve().relative_to(Path(root).resolve())
    except ValueError as exc:
        raise ValueError("La cartella intake deve rimanere all'interno della libreria.") from exc
    return intake


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
    intake = _ensure_intake(root)
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
                    if any(old_original.get(key) != new_original.get(key) for key in ("kind", "path", "sha256", "digest_algorithm")):
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

    if transactions.exists():
        for temporary in transactions.glob(".journal-*.tmp"):
            if temporary.is_symlink() or not temporary.is_file():
                raise RuntimeError(f"File temporaneo di transazione non sicuro: {temporary}")
            temporary.unlink()
    catalog_directory = root / "catalog"
    if catalog_directory.is_dir() and not catalog_directory.is_symlink():
        for temporary in catalog_directory.glob(".materials-*.tmp"):
            if temporary.is_symlink() or not temporary.is_file():
                raise RuntimeError(f"File temporaneo di catalogo non sicuro: {temporary}")
            temporary.unlink()
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
    if not (source_path.is_file() or source_path.is_dir()):
        raise ValueError("Sono ammessi soltanto file e cartelle.")
    _inspect_source(source_path)
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

    intake = _ensure_intake(root)
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
            copied_files, byte_size = _copy_directory_bounded(source_path, staged_source)
            digest = _digest_directory(staged_source)
            stored_path = f"intake/{folder_name}/source"
        else:
            staged_source.mkdir()
            copied_file = staged_source / source_path.name
            counters = {"files": 0, "bytes": 0}
            _copy_file_bounded(source_path, copied_file, counters)
            byte_size = counters["bytes"]
            digest = _digest_file(copied_file)
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
    _ensure_intake(root)
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
