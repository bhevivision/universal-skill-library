#!/usr/bin/env python3
"""Operazioni CRUD sicure sui quattro cataloghi della libreria."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from scripts.validate_library import check_evidence, check_materials

CATALOGS = {
    "skills": ("catalog/skills.json", "skills", "schemas/skills-catalog.schema.json"),
    "capabilities": ("catalog/capabilities.json", "capabilities", "schemas/capabilities-catalog.schema.json"),
    "implementations": ("catalog/implementations.json", "implementations", "schemas/implementations-catalog.schema.json"),
    "materials": ("catalog/materials.json", "materials", "schemas/materials-catalog.schema.json"),
}


class CatalogError(ValueError):
    pass


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"Impossibile leggere {path}: {exc}") from exc


def _registry(root: Path) -> Registry:
    registry = Registry()
    for path in sorted((root / "schemas").glob("*.schema.json")):
        schema = _load_json(path)
        if isinstance(schema, dict) and isinstance(schema.get("$id"), str):
            registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def _load_catalog(root: Path, kind: str):
    if kind not in CATALOGS:
        raise CatalogError(f"Catalogo sconosciuto: {kind}")
    relative, collection, schema_rel = CATALOGS[kind]
    path = root / relative
    if path.is_symlink() or not path.is_file():
        raise CatalogError(f"Catalogo assente o non sicuro: {relative}")
    catalog = _load_json(path)
    schema = _load_json(root / schema_rel)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, registry=_registry(root), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(catalog), key=lambda e: list(e.absolute_path))
    if errors:
        issue = errors[0]
        location = ".".join(map(str, issue.absolute_path)) or "$"
        raise CatalogError(f"{relative}:{location}: {issue.message}")
    entries = catalog[collection]
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(set(ids)):
        raise CatalogError(f"{relative}: identificativi duplicati")
    return path, collection, catalog


def _validate_links(root: Path, kind: str, entry: dict, catalogs: dict):
    if kind == "materials":
        errors = []
        check_materials(root, [entry], errors)
        if errors:
            raise CatalogError(errors[0])
    elif kind == "skills":
        known = {item["id"] for item in catalogs["capabilities"]["capabilities"]}
        missing = set(entry.get("capability_ids", [])) - known
        if missing:
            raise CatalogError("Capacità inesistenti: " + ", ".join(sorted(missing)))

        material_map = {item["id"]: item for item in catalogs["materials"]["materials"]}
        source_material_ids = set(entry.get("source_material_ids", []))
        missing_sources = source_material_ids - set(material_map)
        if missing_sources:
            raise CatalogError("Materiale sorgente inesistente: " + ", ".join(sorted(missing_sources)))

        source_record_id = entry.get("source_record_id")
        if source_record_id:
            source = material_map.get(source_record_id)
            if source is None:
                raise CatalogError("Materiale sorgente inesistente: " + source_record_id)
            classification = source.get("classification", {})
            if classification.get("status") != "classified" or classification.get("kind") != "skill":
                raise CatalogError("Il materiale sorgente deve essere una skill classificata: " + source_record_id)

        verification = entry.get("selection", {}).get("verification", {})
        verification_status = verification.get("status")
        if verification_status in {"passed", "failed", "inconclusive"}:
            errors = []
            check_evidence(
                root,
                verification.get("evidence_refs", []),
                entry["id"],
                verification_status,
                f"verifica skill {entry['id']}",
                errors,
            )
            if errors:
                raise CatalogError(errors[0])

        skill_path = entry.get("path")
        if skill_path:
            candidate = root / skill_path
            if candidate.is_symlink() or not candidate.is_file():
                raise CatalogError("Il percorso SKILL.md non esiste o non è sicuro: " + skill_path)
            try:
                candidate.resolve().relative_to(root.resolve())
            except ValueError as exc:
                raise CatalogError("Il percorso della skill esce dalla libreria.") from exc
    elif kind == "capabilities":
        known = {item["id"] for item in catalogs["skills"]["skills"]}
        missing = set(entry.get("skill_ids", [])) - known
        if missing:
            raise CatalogError("Skill inesistenti: " + ", ".join(sorted(missing)))
    elif kind == "implementations":
        known = {item["id"] for item in catalogs["skills"]["skills"]}
        if entry.get("skill_id") not in known:
            raise CatalogError("Skill associata inesistente: " + str(entry.get("skill_id")))


def _all_catalogs(root: Path):
    root = Path(root).resolve()
    loaded = {}
    for kind in CATALOGS:
        _, _, loaded[kind] = _load_catalog(root, kind)
    return loaded


def _atomic_write(path: Path, value: dict):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def list_entries(root: Path, kind: str):
    root = Path(root).resolve()
    _, collection, catalog = _load_catalog(root, kind)
    return catalog[collection]


def get_entry(root: Path, kind: str, entry_id: str):
    entries = list_entries(root, kind)
    matches = [entry for entry in entries if entry.get("id") == entry_id]
    if not matches:
        raise CatalogError(f"Voce non trovata: {entry_id}")
    return matches[0]


def search_entries(root: Path, kind: str, query: str):
    needle = query.casefold()
    return [entry for entry in list_entries(root, kind)
            if needle in json.dumps(entry, ensure_ascii=False).casefold()]


def put_entry(root: Path, kind: str, entry: dict, *, replace: bool = False):
    root = Path(root).resolve()
    if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
        raise CatalogError("La voce deve essere un oggetto JSON con campo id testuale.")
    catalogs = _all_catalogs(root)
    path, collection, catalog = _load_catalog(root, kind)
    entries = catalog[collection]
    indexes = [i for i, item in enumerate(entries) if item.get("id") == entry["id"]]
    if indexes and not replace:
        raise CatalogError("Identificativo già presente: " + entry["id"])
    if not indexes and replace:
        raise CatalogError("Voce da aggiornare non trovata: " + entry["id"])
    # Verifica schema della singola voce tramite lo schema del catalogo.
    schema = _load_json(root / CATALOGS[kind][2])
    validator = Draft202012Validator(schema, registry=_registry(root), format_checker=FormatChecker())
    candidate = dict(catalog)
    candidate_items = list(entries)
    if indexes:
        candidate_items[indexes[0]] = entry
    else:
        candidate_items.append(entry)
    candidate[collection] = candidate_items
    errors = sorted(validator.iter_errors(candidate), key=lambda e: list(e.absolute_path))
    if errors:
        issue = errors[0]
        raise CatalogError(f"Voce non valida: {issue.message}")
    _validate_links(root, kind, entry, catalogs)
    catalog[collection] = candidate_items
    _atomic_write(path, catalog)
    return entry


def remove_entry(root: Path, kind: str, entry_id: str):
    root = Path(root).resolve()
    catalogs = _all_catalogs(root)
    path, collection, catalog = _load_catalog(root, kind)
    matches = [item for item in catalog[collection] if item.get("id") == entry_id]
    if not matches:
        raise CatalogError(f"Voce non trovata: {entry_id}")
    if kind == "skills":
        if any(entry_id in item.get("skill_ids", []) for item in catalogs["capabilities"]["capabilities"]):
            raise CatalogError("Impossibile eliminare: la skill è referenziata da una capacità.")
        if any(item.get("skill_id") == entry_id for item in catalogs["implementations"]["implementations"]):
            raise CatalogError("Impossibile eliminare: la skill ha implementazioni associate.")
    if kind == "capabilities" and any(entry_id in item.get("capability_ids", []) for item in catalogs["skills"]["skills"]):
        raise CatalogError("Impossibile eliminare: la capacità è usata da una skill.")
    if kind == "materials" and any(
        item.get("source_record_id") == entry_id
        or entry_id in item.get("source_material_ids", [])
        for item in catalogs["skills"]["skills"]
    ):
        raise CatalogError("Impossibile eliminare: il materiale è registrato come fonte di una skill.")
    catalog[collection] = [item for item in catalog[collection] if item.get("id") != entry_id]
    _atomic_write(path, catalog)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gestione dei cataloghi della libreria.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("list", "show", "search", "add", "update", "remove"):
        p = sub.add_parser(command)
        p.add_argument("catalog", choices=sorted(CATALOGS))
        if command in {"show", "remove"}:
            p.add_argument("id")
        if command == "search":
            p.add_argument("query")
        if command in {"add", "update"}:
            p.add_argument("--entry", required=True, help="Oggetto JSON completo della voce")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "list":
            result = list_entries(root, args.catalog)
        elif args.command == "show":
            result = get_entry(root, args.catalog, args.id)
        elif args.command == "search":
            result = search_entries(root, args.catalog, args.query)
        elif args.command in {"add", "update"}:
            entry = json.loads(args.entry)
            result = put_entry(root, args.catalog, entry, replace=args.command == "update")
        else:
            remove_entry(root, args.catalog, args.id)
            result = {"removed": args.id}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (CatalogError, json.JSONDecodeError, OSError) as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
