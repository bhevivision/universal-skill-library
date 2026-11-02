#!/usr/bin/env python3
"""Controlli strutturali e di coerenza della libreria universale delle skill."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker\nimport yaml
from referencing import Registry, Resource
CATALOGS={
 "catalog/capabilities.json":("capabilities","schemas/capabilities-catalog.schema.json","schemas/capability.schema.json"),
 "catalog/skills.json":("skills","schemas/skills-catalog.schema.json","schemas/skill-entry.schema.json"),
 "catalog/implementations.json":("implementations","schemas/implementations-catalog.schema.json","schemas/implementation.schema.json")}
def read_json(root,rel,errors):
 p=root/rel
 if not p.is_file(): errors.append(f"{rel}: file non trovato"); return None
 try: return json.loads(p.read_text(encoding="utf-8"))
 except (OSError,UnicodeError,json.JSONDecodeError) as e: errors.append(f"{rel}: JSON non valido ({e})"); return None
def schema_registry(root):
 registry=Registry()
 for path in sorted((root/"schemas").glob("*.schema.json")):
  try:
   schema=json.loads(path.read_text(encoding="utf-8"))
   if isinstance(schema,dict) and isinstance(schema.get("$id"),str):
    registry=registry.with_resource(schema["$id"],Resource.from_contents(schema))
  except (OSError,UnicodeError,json.JSONDecodeError):
   continue
 return registry
def check_schema(root,value,rel,source,errors):
 schema=read_json(root,rel,errors)
 if schema is None:return
 try:
  Draft202012Validator.check_schema(schema)
  for issue in Draft202012Validator(schema,registry=schema_registry(root),format_checker=FormatChecker()).iter_errors(value):
   where=".".join(map(str,issue.absolute_path)) or "$"; errors.append(f"{source}:{where}: {issue.message}")
 except Exception as e: errors.append(f"{rel}: schema non valido ({e})")
def safe_path(root,rel):
 if not isinstance(rel,str) or not rel or "\\" in rel:return None
 p=(root/rel).resolve()
 try:p.relative_to(root.resolve())
 except ValueError:return None
 return p
def check_evidence(root,refs,subject,expected_result,label,errors):
 if not refs:errors.append(f"{label}: verifica dichiarata senza prove");return
 for ref in refs:
  if not isinstance(ref,str) or not ref.startswith("tests/evidence/"):errors.append(f"{label}: prova fuori da tests/evidence/: {ref}");continue
  p=safe_path(root,ref)
  if p is None or not p.is_file():errors.append(f"{label}: prova non trovata o percorso non sicuro: {ref}");continue
  try: proof=json.loads(p.read_text(encoding="utf-8"))
  except (OSError,UnicodeError,json.JSONDecodeError) as e:errors.append(f"{ref}: prova JSON non valida ({e})");continue
  check_schema(root,proof,"schemas/evidence.schema.json",ref,errors)
  if isinstance(proof,dict):
   if proof.get("result")!=expected_result:errors.append(f"{ref}: esito prova diverso dall'esito dichiarato {expected_result}")
   if proof.get("subject")!=subject:errors.append(f"{ref}: la prova riguarda {proof.get('subject')!r}, non {subject!r}")
class UniqueKeyLoader(yaml.SafeLoader):
 def construct_mapping(self,node,deep=False):
  mapping={}
  for key_node,value_node in node.value:
   key=self.construct_object(key_node,deep=deep)
   if key in mapping:raise yaml.constructor.ConstructorError("mapping",node.start_mark,f"chiave YAML duplicata: {key}",key_node.start_mark)
   mapping[key]=self.construct_object(value_node,deep=deep)
  return mapping
def frontmatter(p):
 t=p.read_text(encoding="utf-8")
 if not t.startswith("---\\n"):raise ValueError("frontmatter YAML assente o delimitatore iniziale mancante")
 end=t.find("\\n---",4)
 if end<0:raise ValueError("delimitatore finale del frontmatter mancante")
 values=yaml.load(t[4:end],Loader=UniqueKeyLoader)
 if not isinstance(values,dict):raise ValueError("frontmatter YAML deve contenere una mappa")
 name,description=values.get("name"),values.get("description")
 if not isinstance(name,str) or not name.strip():raise ValueError("campo name mancante o non testuale")
 if not isinstance(description,str) or not description.strip():raise ValueError("campo description mancante o non testuale")
 if len(name)>64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",name):raise ValueError("campo name non conforme al formato Agent Skills")
 if len(description)>1024:raise ValueError("campo description supera 1024 caratteri")
 return name,description
def validate_repository(root):
 root=Path(root).resolve(); errors=[]; catalogs={}
 for rel,(collection,catalog_schema,entry_schema) in CATALOGS.items():
  data=read_json(root,rel,errors)
  if data is None:continue
  check_schema(root,data,catalog_schema,rel,errors)
  if isinstance(data,dict) and isinstance(data.get(collection),list):
   catalogs[collection]=data[collection]
   for i,item in enumerate(data[collection]):check_schema(root,item,entry_schema,f"{rel}:{i}",errors)
 caps,skills,impls=catalogs.get("capabilities",[]),catalogs.get("skills",[]),catalogs.get("implementations",[])
 def index(items,label):
  result={}
  for item in items:
   if not isinstance(item,dict) or not isinstance(item.get("id"),str):continue
   key=item["id"]
   if key in result:errors.append(f"{label}: identificativo duplicato {key}")
   result[key]=item
  return result
 capmap,skillmap=index(caps,"capacità"),index(skills,"skill");index(impls,"implementazioni")
 for skill in skills:
  if not isinstance(skill,dict):continue
  sid,rel=skill.get("id","<senza-id>"),skill.get("path"); package=safe_path(root,rel)
  if package is None or not package.is_file():errors.append(f"skill {sid}: SKILL.md non trovato o percorso non sicuro ({rel})")
  else:
   try:
    name,description=frontmatter(package)
    if name!=package.parent.name:errors.append(f"skill {sid}: name del frontmatter ({name!r}) non coincide con la cartella ({package.parent.name!r})")
    if not description:errors.append(f"skill {sid}: description mancante nel frontmatter")
   except yaml.YAMLError as e:errors.append(f"skill {sid}: frontmatter YAML non valido ({e})")
   except ValueError as e:
    message=str(e)
    if "chiave YAML duplicata" in message:errors.append(f"skill {sid}: {message}")
    else:errors.append(f"skill {sid}: frontmatter non valido ({message})")
   except (OSError,UnicodeError) as e:errors.append(f"skill {sid}: impossibile leggere SKILL.md ({e})")
  for cid in skill.get("capability_ids",[]):
   cap=capmap.get(cid)
   if cap is None:errors.append(f"skill {sid}: capacità inesistente {cid}")
   elif sid not in cap.get("skill_ids",[]):errors.append(f"skill {sid}: collegamento non reciproco nella capacità {cid}")
  if skill.get("scope")=="platform" and not skill.get("platforms"):errors.append(f"skill {sid}: scope=platform richiede almeno una piattaforma")
  sel=skill.get("selection",{}); ver=sel.get("verification",{}) if isinstance(sel,dict) else {}
  if ver.get("status") in {"passed","failed","inconclusive"}:check_evidence(root,ver.get("evidence_refs",[]),sid,ver.get("status"),f"skill {sid}",errors)
  if skill.get("lifecycle")=="stable" and ver.get("status")!="passed":errors.append(f"skill {sid}: lifecycle=stable richiede verifica superata e documentata")
 for cap in caps:
  if not isinstance(cap,dict):continue
  cid=cap.get("id","<senza-id>")
  for sid in cap.get("skill_ids",[]):
   skill=skillmap.get(sid)
   if skill is None:errors.append(f"capacità {cid}: skill inesistente {sid}")
   elif cid not in skill.get("capability_ids",[]):errors.append(f"capacità {cid}: collegamento non reciproco nella skill {sid}")
  for related in cap.get("related_capabilities",[]):
   if related not in capmap:errors.append(f"capacità {cid}: capacità collegata inesistente {related}")
 for impl in impls:
  if not isinstance(impl,dict):continue
  iid,sid=impl.get("id","<senza-id>"),impl.get("skill_id"); skill=skillmap.get(sid)
  if skill is None:errors.append(f"implementazione {iid}: skill inesistente {sid}")
  else:
   if impl.get("skill_version")!=skill.get("version"):errors.append(f"implementazione {iid}: versione skill incompatibile con {sid}")
   if skill.get("scope")=="platform" and impl.get("platform") not in skill.get("platforms",[]):errors.append(f"implementazione {iid}: piattaforma {impl.get('platform')} incompatibile con la skill {sid}")
  rel=impl.get("path"); mp=safe_path(root,rel)
  if mp is None or not mp.is_file():errors.append(f"implementazione {iid}: manifest non trovato o percorso non sicuro ({rel})")
  else:
   manifest=read_json(root,rel,errors)
   if manifest is not None:check_schema(root,manifest,"schemas/implementation-manifest.schema.json",rel,errors)
   if isinstance(manifest,dict):
    for field in ("id","skill_id","skill_version","platform"):
     if manifest.get(field)!=impl.get(field):errors.append(f"implementazione {iid}: manifest non coerente nel campo {field}")
  ver=impl.get("verification",{})
  if impl.get("status")=="verified" and ver.get("status")!="passed":errors.append(f"implementazione {iid}: status=verified richiede verification.status=passed")
  if impl.get("status")=="verified" or ver.get("status") in {"passed","failed","inconclusive"}:check_evidence(root,ver.get("evidence_refs",[]),iid,ver.get("status"),f"implementazione {iid}",errors)
 return errors
def main():
 parser=argparse.ArgumentParser(description="Controlla cataloghi, skill, implementazioni e prove.")
 parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
 errors=validate_repository(args.root)
 if errors:
  print(f"CONTROLLO FALLITO: {len(errors)} problema/i")
  for e in errors:print(f"- {e}")
  return 1
 print("CONTROLLO SUPERATO: cataloghi, collegamenti, pacchetti e prove coerenti.");return 0
if __name__=="__main__":sys.exit(main())
