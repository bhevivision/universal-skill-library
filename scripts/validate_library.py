#!/usr/bin/env python3
"""Controlli strutturali e di coerenza della libreria universale delle skill."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
import yaml
from referencing import Registry, Resource

CATALOGS = {
    "catalog/capabilities.json": ("capabilities", "schemas/capabilities-catalog.schema.json", "schemas/capability.schema.json"),
    "catalog/materials.json": ("materials", "schemas/materials-catalog.schema.json", "schemas/material-record.schema.json"),
    "catalog/skills.json": ("skills", "schemas/skills-catalog.schema.json", "schemas/skill-entry.schema.json"),
    "catalog/implementations.json": ("implementations", "schemas/implementations-catalog.schema.json", "schemas/implementation.schema.json"),
}


def read_json(root, rel, errors):
    path = root / rel
    if not path.is_file():
        errors.append(f"{rel}: file non trovato")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{rel}: JSON non valido ({exc})")
        return None


def schema_registry(root):
    registry = Registry()
    for path in sorted((root / "schemas").glob("*.schema.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(schema, dict) and isinstance(schema.get("$id"), str):
                registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
    return registry


def check_schema(root, value, rel, source, errors):
    schema = read_json(root, rel, errors)
    if schema is None:
        return
    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, registry=schema_registry(root), format_checker=FormatChecker())
        for issue in validator.iter_errors(value):
            where = ".".join(map(str, issue.absolute_path)) or "$"
            errors.append(f"{source}:{where}: {issue.message}")
    except Exception as exc:
        errors.append(f"{rel}: schema non valido ({exc})")


def safe_path(root, rel):
    if not isinstance(rel, str) or not rel or "\\" in rel:
        return None
    candidate = root / rel
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    current = candidate
    while current != root:
        if current.is_symlink():
            return None
        current = current.parent
    path = candidate.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_directory(path):
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*"), key=lambda entry: entry.relative_to(path).as_posix()):
        if item.is_symlink():
            raise ValueError(f"collegamento simbolico non ammesso: {item}")
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


def digest_directory_legacy(path):
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"collegamento simbolico non ammesso: {item}")
        if item.is_file():
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            with item.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            digest.update(b"\0")
    return digest.hexdigest()


def check_materials(root, materials, errors):
    material_map = {}
    for material in materials:
        if not isinstance(material, dict):
            continue
        mid = material.get("id", "<senza-id>")
        if mid in material_map:
            errors.append(f"materiali: identificativo duplicato {mid}")
        material_map[mid] = material
        license_record = material.get("license")
        if isinstance(license_record, dict) and license_record.get("review_status") in {"reviewed", "needs_human_review"}:
            license_status = license_record.get("status")
            expected_license_result = "passed" if license_status in {"identified", "not_declared"} else "inconclusive"
            check_evidence(
                root,
                license_record.get("evidence_refs", []),
                f"material.{mid}.license",
                expected_license_result,
                f"licenza materiale {mid}",
                errors,
            )
        acquisition = material.get("acquisition", {})
        original = acquisition.get("original", {}) if isinstance(acquisition, dict) else {}
        kind, rel = original.get("kind"), original.get("path")
        uri = original.get("uri")
        status = acquisition.get("status")
        if status == "preserved" and not rel and not uri:
            errors.append(f"materiale {mid}: stato preserved senza originale locale o riferimento remoto")
        if status == "preserved" and rel and not original.get("sha256"):
            errors.append(f"materiale {mid}: originale locale conservato senza impronta SHA-256")
        if kind == "remote_reference":
            if not uri:
                errors.append(f"materiale {mid}: riferimento remoto senza URI")
            continue
        if not rel:
            continue
        if not rel.startswith("intake/") or ".." in Path(rel).parts:
            errors.append(f"materiale {mid}: l'originale locale deve trovarsi sotto intake/ senza risalire le cartelle: {rel}")
            continue
        path = safe_path(root, rel)
        if path is None or not path.exists():
            errors.append(f"materiale {mid}: originale non trovato o percorso non sicuro ({rel})")
            continue
        if kind in {"file", "archive"} and not path.is_file():
            errors.append(f"materiale {mid}: il tipo {kind} richiede un file originale ({rel})")
            continue
        if kind == "package" and not (path.is_file() or path.is_dir()):
            errors.append(f"materiale {mid}: il pacchetto deve essere un file o una cartella ({rel})")
            continue
        if kind == "directory" and not path.is_dir():
            errors.append(f"materiale {mid}: il tipo directory richiede una cartella originale ({rel})")
            continue
        try:
            algorithm = original.get("digest_algorithm")
            if path.is_dir():
                if algorithm not in {None, "sha256-tree-v2"}:
                    errors.append(f"materiale {mid}: algoritmo impronta non supportato ({algorithm})")
                    continue
                actual = digest_directory_legacy(path) if algorithm is None else digest_directory(path)
            else:
                if algorithm not in {None, "sha256-file-v1"}:
                    errors.append(f"materiale {mid}: algoritmo impronta non supportato ({algorithm})")
                    continue
                actual = digest_file(path)
            expected = original.get("sha256")
            if expected and actual != expected:
                errors.append(f"materiale {mid}: impronta SHA-256 dell'originale non corrispondente")
        except (OSError, ValueError) as exc:
            errors.append(f"materiale {mid}: impossibile verificare l'originale ({exc})")
    return material_map


def check_evidence(root, refs, subject, expected_result, label, errors):
    if not refs:
        errors.append(f"{label}: verifica dichiarata senza prove")
        return
    for ref in refs:
        if not isinstance(ref, str) or not ref.startswith("tests/evidence/"):
            errors.append(f"{label}: prova fuori da tests/evidence/: {ref}")
            continue
        path = safe_path(root, ref)
        if path is None or not path.is_file():
            errors.append(f"{label}: prova non trovata o percorso non sicuro: {ref}")
            continue
        try:
            proof = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{ref}: prova JSON non valida ({exc})")
            continue
        check_schema(root, proof, "schemas/evidence.schema.json", ref, errors)
        if isinstance(proof, dict):
            if proof.get("result") != expected_result:
                errors.append(f"{ref}: esito prova diverso dall'esito dichiarato {expected_result}")
            if proof.get("subject") != subject:
                errors.append(f"{ref}: la prova riguarda {proof.get('subject')!r}, non {subject!r}")


class DuplicateFrontmatterKeyError(ValueError):
    pass


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise DuplicateFrontmatterKeyError(f"chiave YAML duplicata: {key}")
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("frontmatter YAML assente o delimitatore iniziale mancante")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("delimitatore finale del frontmatter mancante")
    values = yaml.load(text[4:end], Loader=UniqueKeyLoader)
    if not isinstance(values, dict):
        raise ValueError("frontmatter YAML deve contenere una mappa")
    name, description = values.get("name"), values.get("description")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("campo name mancante o non testuale")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("campo description mancante o non testuale")
    if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("campo name non conforme al formato Agent Skills")
    if len(description) > 1024:
        raise ValueError("campo description supera 1024 caratteri")
    return name, description


def validate_repository(root):
    root = Path(root).resolve()
    errors = []
    catalogs = {}
    for rel, (collection, catalog_schema, entry_schema) in CATALOGS.items():
        data = read_json(root, rel, errors)
        if data is None:
            continue
        check_schema(root, data, catalog_schema, rel, errors)
        if isinstance(data, dict) and isinstance(data.get(collection), list):
            catalogs[collection] = data[collection]
            for index, item in enumerate(data[collection]):
                check_schema(root, item, entry_schema, f"{rel}:{index}", errors)

    capabilities = catalogs.get("capabilities", [])
    materials = catalogs.get("materials", [])
    skills = catalogs.get("skills", [])
    implementations = catalogs.get("implementations", [])

    def index(items, label):
        result = {}
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            key = item["id"]
            if key in result:
                errors.append(f"{label}: identificativo duplicato {key}")
            result[key] = item
        return result

    capmap = index(capabilities, "capacità")
    materialmap = check_materials(root, materials, errors)
    skillmap = index(skills, "skill")
    index(implementations, "implementazioni")

    for skill in skills:
        if not isinstance(skill, dict):
            continue
        sid = skill.get("id", "<senza-id>")
        source_record_id = skill.get("source_record_id")
        rel = skill.get("path")
        if source_record_id:
            material = materialmap.get(source_record_id)
            if material is None:
                errors.append(f"skill {sid}: scheda materiale inesistente {source_record_id}")
            else:
                classification = material.get("classification", {})
                if classification.get("kind") != "skill" or classification.get("status") != "classified":
                    errors.append(f"skill {sid}: il materiale collegato non è classificato come skill")
        elif rel:
            package = safe_path(root, rel)
            if package is None or not package.is_file():
                errors.append(f"skill {sid}: SKILL.md non trovato o percorso non sicuro ({rel})")
            else:
                try:
                    name, _ = frontmatter(package)
                    if name != package.parent.name:
                        errors.append(f"skill {sid}: name del frontmatter ({name!r}) non coincide con la cartella ({package.parent.name!r})")
                except DuplicateFrontmatterKeyError as exc:
                    errors.append(f"skill {sid}: {exc}")
                except yaml.YAMLError as exc:
                    errors.append(f"skill {sid}: frontmatter YAML non valido ({exc})")
                except ValueError as exc:
                    errors.append(f"skill {sid}: frontmatter non valido ({exc})")
                except (OSError, UnicodeError) as exc:
                    errors.append(f"skill {sid}: impossibile leggere SKILL.md ({exc})")

        for capability_id in skill.get("capability_ids", []):
            capability = capmap.get(capability_id)
            if capability is None:
                errors.append(f"skill {sid}: capacità inesistente {capability_id}")
            elif sid not in capability.get("skill_ids", []):
                errors.append(f"skill {sid}: collegamento non reciproco nella capacità {capability_id}")
        if skill.get("scope") == "platform" and not skill.get("platforms"):
            errors.append(f"skill {sid}: scope=platform richiede almeno una piattaforma")
        selection = skill.get("selection", {})
        verification = selection.get("verification", {}) if isinstance(selection, dict) else {}
        if verification.get("status") in {"passed", "failed", "inconclusive"}:
            check_evidence(root, verification.get("evidence_refs", []), sid, verification.get("status"), f"skill {sid}", errors)
        if skill.get("lifecycle") == "stable" and verification.get("status") != "passed":
            errors.append(f"skill {sid}: lifecycle=stable richiede verifica superata e documentata")

    for capability in capabilities:
        if not isinstance(capability, dict):
            continue
        cid = capability.get("id", "<senza-id>")
        for sid in capability.get("skill_ids", []):
            skill = skillmap.get(sid)
            if skill is None:
                errors.append(f"capacità {cid}: skill inesistente {sid}")
            elif cid not in skill.get("capability_ids", []):
                errors.append(f"capacità {cid}: collegamento non reciproco nella skill {sid}")
        for related in capability.get("related_capabilities", []):
            if related not in capmap:
                errors.append(f"capacità {cid}: capacità collegata inesistente {related}")

    for implementation in implementations:
        if not isinstance(implementation, dict):
            continue
        iid = implementation.get("id", "<senza-id>")
        sid = implementation.get("skill_id")
        skill = skillmap.get(sid)
        if skill is None:
            errors.append(f"implementazione {iid}: skill inesistente {sid}")
        else:
            if implementation.get("skill_version") != skill.get("version"):
                errors.append(f"implementazione {iid}: versione skill incompatibile con {sid}")
            if skill.get("scope") == "platform" and implementation.get("platform") not in skill.get("platforms", []):
                errors.append(f"implementazione {iid}: piattaforma {implementation.get('platform')} incompatibile con la skill {sid}")
        manifest_path = implementation.get("path")
        manifest_file = safe_path(root, manifest_path)
        if manifest_file is None or not manifest_file.is_file():
            errors.append(f"implementazione {iid}: manifest non trovato o percorso non sicuro ({manifest_path})")
        else:
            manifest = read_json(root, manifest_path, errors)
            if manifest is not None:
                check_schema(root, manifest, "schemas/implementation-manifest.schema.json", manifest_path, errors)
            if isinstance(manifest, dict):
                for field in ("id", "skill_id", "skill_version", "platform"):
                    if manifest.get(field) != implementation.get(field):
                        errors.append(f"implementazione {iid}: manifest non coerente nel campo {field}")
        verification = implementation.get("verification", {})
        if implementation.get("status") == "verified" and verification.get("status") != "passed":
            errors.append(f"implementazione {iid}: status=verified richiede verification.status=passed")
        if implementation.get("status") == "verified" or verification.get("status") in {"passed", "failed", "inconclusive"}:
            check_evidence(root, verification.get("evidence_refs", []), iid, verification.get("status"), f"implementazione {iid}", errors)

    return errors


def main():
    parser = argparse.ArgumentParser(description="Controlla acquisizioni, cataloghi, collegamenti, implementazioni e prove.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate_repository(args.root)
    if errors:
        print(f"CONTROLLO FALLITO: {len(errors)} problema/i")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CONTROLLO SUPERATO: acquisizioni, cataloghi, collegamenti, implementazioni e prove coerenti.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
