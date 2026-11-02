#!/usr/bin/env python3
"""Componente indipendente per acquisire e conservare materiali senza eseguirli."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
MATERIAL_SCHEMA = "schemas/material-record.schema.json"


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
    for item in sorted(Path(path).rglob("*")):
        if item.is_symlink():
            raise ValueError(f"Collegamento simbolico non ammesso: {item}")
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            with item.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            digest.update(b"\0")
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
    schema_path = root / MATERIAL_SCHEMA
    if not schema_path.is_file():
        raise FileNotFoundError(f"Schema della scheda materiale non trovato: {schema_path}")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
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
        "acquisition": {
            "status": status,
            "acquired_at": _timestamp(),
            "method": method,
            "original": original
        },
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


def _acquisition_lock(root):
    lock_path = root / ".materials-acquisition.lock"
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError("È già in corso un'altra acquisizione. Riprovare dopo la sua conclusione.") from exc
    os.close(descriptor)
    return lock_path


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
    inferred = _infer_kind(source_path)
    material_kind = kind or inferred
    allowed = {"file", "directory", "archive", "package", "unknown"}
    if material_kind not in allowed:
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
    try:
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"La destinazione esiste già e non verrà sovrascritta: {destination}")
        catalog, _ = _load_catalog(root)
        if any(isinstance(item, dict) and item.get("id") == material_id for item in catalog["materials"]):
            raise ValueError(f"Identificativo già presente nel catalogo: {material_id}")

        stage = Path(tempfile.mkdtemp(prefix=f".{folder_name}-", dir=intake))
        staged_source = stage / "source"
        if source_path.is_dir():
            shutil.copytree(source_path, staged_source, copy_function=shutil.copy2)
            digest = _digest_directory(staged_source)
            byte_size = _directory_size(staged_source)
            stored_path = f"intake/{folder_name}/source"
        else:
            staged_source.mkdir()
            copied_file = staged_source / source_path.name
            shutil.copy2(source_path, copied_file)
            digest = _digest_file(copied_file)
            byte_size = copied_file.stat().st_size
            stored_path = f"intake/{folder_name}/source/{source_path.name}"

        if source_path.is_file() and _digest_file(source_path) != digest:
            raise OSError("La copia acquisita non coincide con il file sorgente.")
        if source_path.is_dir() and _digest_directory(source_path) != digest:
            raise OSError("La copia acquisita non coincide con la cartella sorgente.")

        record = _base_record(
            material_id, name or source_path.name, description, method, source_label,
            "preserved",
            {"kind": material_kind, "path": stored_path, "sha256": digest, "byte_size": byte_size}
        )
        _validate_record(root, record)
        os.rename(stage, destination)
        stage = None
        try:
            _append_record(root, record)
        except Exception:
            shutil.rmtree(destination, ignore_errors=True)
            raise
        return record
    finally:
        if stage is not None:
            shutil.rmtree(stage, ignore_errors=True)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def acquire_remote_material(root, material_id, uri, *, name=None, description=None,
                            method="remote_reference", source_label=None):
    """Registra un riferimento remoto senza dichiarare di averne una copia locale."""
    _validate_id(material_id)
    parsed = urlparse(uri) if isinstance(uri, str) else None
    if parsed is None or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Il riferimento remoto deve essere un URI HTTP o HTTPS valido.")
    root = Path(root).resolve()
    record = _base_record(
        material_id, name, description, method, source_label,
        "received", {"kind": "remote_reference", "uri": uri}
    )
    lock_path = _acquisition_lock(root)
    try:
        _append_record(root, record)
        return record
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def main():
    parser = argparse.ArgumentParser(description="Acquisisce un materiale senza eseguirlo o modificarlo.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Cartella principale della libreria.")
    parser.add_argument("--id", required=True, dest="material_id", help="Identificativo, ad esempio acq.nuova-skill.")
    parser.add_argument("--source", type=Path, help="File o cartella locale da acquisire.")
    parser.add_argument("--uri", help="Riferimento remoto HTTP o HTTPS da registrare.")
    parser.add_argument("--name", help="Nome descrittivo facoltativo.")
    parser.add_argument("--description", help="Descrizione facoltativa.")
    parser.add_argument("--method", default=None, help="Metodo di acquisizione.")
    parser.add_argument("--source-label", help="Provenienza dichiarata.")
    parser.add_argument("--kind", choices=["file", "directory", "archive", "package", "unknown"])
    args = parser.parse_args()
    if bool(args.source) == bool(args.uri):
        parser.error("Specificare uno e un solo elemento tra --source e --uri.")
    try:
        if args.uri:
            record = acquire_remote_material(
                args.root, args.material_id, args.uri, name=args.name,
                description=args.description, method=args.method or "remote_reference",
                source_label=args.source_label
            )
        else:
            record = acquire_material(
                args.root, args.source, args.material_id, name=args.name,
                description=args.description, method=args.method or "local_copy",
                source_label=args.source_label, kind=args.kind
            )
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ACQUISIZIONE FALLITA: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
