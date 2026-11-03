import json, shutil, tempfile, unittest
from pathlib import Path
from scripts.validate_library import validate_repository

def write_json(root,rel,value):
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2),encoding="utf-8")
def make_repo(root):
 shutil.copytree(Path(__file__).resolve().parents[1]/"schemas",root/"schemas")
 d=root/"skills/pdf-analyze";d.mkdir(parents=True)
 (d/"SKILL.md").write_text("---\nname: pdf-analyze\ndescription: Analizza documenti PDF.\n---\n# Istruzioni\n",encoding="utf-8")
 (root/"implementations/python/pdf-analyze").mkdir(parents=True)
 proof={"id":"proof.skill.001","subject":"document.pdf-analyze","result":"passed","tested_at":"2026-11-02T10:00:00Z","command":"python -m unittest","summary":"Test isolato superato."}
 write_json(root,"tests/evidence/skill.json",proof)
 write_json(root,"tests/evidence/implementation.json",dict(proof,id="proof.impl.001",subject="python.pdf-analyze"))
 write_json(root,"catalog/materials.json",{"catalog_version":"1.0","materials":[]})
 write_json(root,"catalog/capabilities.json",{"catalog_version":"1.0","capabilities":[{"id":"document.pdf.analyze","name":"Analisi PDF","description":"Analizzare PDF.","category":"documenti","expected_result":"Sintesi verificabile.","verification_criteria":["Riferimenti alle pagine"],"skill_ids":["document.pdf-analyze"],"status":"active"}]})
 write_json(root,"catalog/skills.json",{"catalog_version":"1.0","skills":[{"id":"document.pdf-analyze","path":"skills/pdf-analyze/SKILL.md","capability_ids":["document.pdf.analyze"],"scope":"universal","version":"1.0.0","lifecycle":"stable","platforms":[],"tags":["pdf"],"selection":{"task_signals":["analizzare PDF"],"inputs":[{"name":"documento","description":"File PDF","required":True,"format":"application/pdf"}],"outputs":[{"name":"sintesi","description":"Sintesi con pagine","format":"markdown"}],"prerequisites":[],"constraints":[],"risk_level":"low","verification":{"status":"passed","last_checked":"2026-11-02T10:00:00Z","evidence_refs":["tests/evidence/skill.json"]}}}]})
 write_json(root,"catalog/implementations.json",{"catalog_version":"1.0","implementations":[{"id":"python.pdf-analyze","skill_id":"document.pdf-analyze","skill_version":"1.0.0","platform":"python","path":"implementations/python/pdf-analyze/manifest.json","requirements":["Python 3.11+"],"tool_requirements":["pypdf"],"permissions_required":["read_input_file"],"agent_compatibility":{"mode":"specific","agents":[{"agent":"codex","versions":">=1.0"}]},"status":"verified","verification":{"status":"passed","last_checked":"2026-11-02T10:00:00Z","evidence_refs":["tests/evidence/implementation.json"]}}]})
 write_json(root,"implementations/python/pdf-analyze/manifest.json",{"id":"python.pdf-analyze","skill_id":"document.pdf-analyze","skill_version":"1.0.0","platform":"python"})

class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);make_repo(self.root)
 def tearDown(self):self.temp.cleanup()
 def change(self,rel,fn):
  p=self.root/rel;data=json.loads(p.read_text());fn(data);p.write_text(json.dumps(data))
 def test_accepts_valid_catalogs_and_proofs(self):self.assertEqual(validate_repository(self.root),[])
 def test_rejects_missing_capability(self):
  self.change("catalog/skills.json",lambda d:d["skills"][0].update(capability_ids=["missing.capability"]))
  self.assertTrue(any("missing.capability" in e for e in validate_repository(self.root)))
 def test_rejects_verified_without_proof(self):
  self.change("catalog/implementations.json",lambda d:d["implementations"][0]["verification"].update(evidence_refs=[]))
  self.assertTrue(any("evidence" in e.lower() for e in validate_repository(self.root)))
 def test_rejects_platform_mismatch(self):
  def edit(d):d["skills"][0].update(scope="platform",platforms=["windows"])
  self.change("catalog/skills.json",edit)
  self.assertTrue(any("piattaforma" in e.lower() for e in validate_repository(self.root)))
 def test_rejects_folder_name_mismatch(self):
  (self.root/"skills/pdf-analyze/SKILL.md").write_text("---\nname: other-name\ndescription: Test.\n---\n")
  self.assertTrue(any("name" in e.lower() for e in validate_repository(self.root)))
 def test_requires_evidence_for_failed_verification_too(self):
  def edit(d):
   d["skills"][0]["lifecycle"]="experimental"
   d["skills"][0]["selection"]["verification"].update(status="failed",evidence_refs=[])
  self.change("catalog/skills.json",edit)
  self.assertTrue(any("evidence" in e.lower() for e in validate_repository(self.root)))
 def test_rejects_duplicate_ids(self):
  self.change("catalog/capabilities.json",lambda d:d["capabilities"].append(dict(d["capabilities"][0])))
  self.assertTrue(any("duplicato" in e.lower() for e in validate_repository(self.root)))
 def test_rejects_missing_proof_file(self):
  def edit(d):d["skills"][0]["selection"]["verification"].update(evidence_refs=["tests/evidence/missing.json"])
  self.change("catalog/skills.json",edit)
  self.assertTrue(any("prova non trovata" in e.lower() for e in validate_repository(self.root)))
 def test_rejects_manifest_mismatch(self):
  p=self.root/"implementations/python/pdf-analyze/manifest.json";d=json.loads(p.read_text());d["platform"]="windows";p.write_text(json.dumps(d))
  self.assertTrue(any("manifest non coerente" in e.lower() for e in validate_repository(self.root)))
 def test_rejects_unknown_catalog_field(self):
  self.change("catalog/skills.json",lambda d:d["skills"][0].update(unapproved_field=True))
  self.assertTrue(any("additional properties" in e.lower() for e in validate_repository(self.root)))

 def test_accepts_not_run_verification_without_date_or_evidence(self):
  def edit(d):
   d["skills"][0]["lifecycle"]="unverified"
   d["skills"][0]["selection"]["verification"]={"status":"not_run","evidence_refs":[]}
  self.change("catalog/skills.json",edit)
  self.assertEqual(validate_repository(self.root),[])
 def test_accepts_multiline_yaml_description(self):
  p=self.root/"skills/pdf-analyze/SKILL.md"
  p.write_text("---\nname: pdf-analyze\ndescription: >-\n  Analizza documenti PDF\n  mantenendo i riferimenti alle pagine.\n---\n# Istruzioni\n",encoding="utf-8")
  self.assertEqual(validate_repository(self.root),[])
 def test_accepts_quoted_yaml_frontmatter(self):
  p=self.root/"skills/pdf-analyze/SKILL.md"
  p.write_text('---\nname: "pdf-analyze"\ndescription: \'Analizza PDF: testo e tabelle.\'\n---\n# Istruzioni\n',encoding="utf-8")
  self.assertEqual(validate_repository(self.root),[])
 def test_rejects_malformed_yaml_frontmatter(self):
  p=self.root/"skills/pdf-analyze/SKILL.md"
  p.write_text("---\nname: [pdf-analyze\ndescription: Test\n---\n",encoding="utf-8")
  self.assertTrue(any("frontmatter YAML non valido" in e for e in validate_repository(self.root)))
 def test_rejects_duplicate_frontmatter_keys(self):
  p=self.root/"skills/pdf-analyze/SKILL.md"
  p.write_text("---\nname: pdf-analyze\nname: other\ndescription: Test\n---\n",encoding="utf-8")
  self.assertTrue(any("chiave YAML duplicata" in e for e in validate_repository(self.root)))
 def test_accepts_agent_independent_implementation(self):
  self.change("catalog/implementations.json",lambda d:d["implementations"][0].update(agent_compatibility={"mode":"any","agents":[]}))
  self.assertEqual(validate_repository(self.root),[])
 def test_rejects_empty_specific_agent_compatibility(self):
  self.change("catalog/implementations.json",lambda d:d["implementations"][0].update(agent_compatibility={"mode":"specific","agents":[]}))
  self.assertTrue(any("agent_compatibility" in e for e in validate_repository(self.root)))

 def test_rejects_date_for_not_run_verification(self):
  def edit(d):
   d["skills"][0]["lifecycle"]="unverified"
   d["skills"][0]["selection"]["verification"]={"status":"not_run","last_checked":"2026-11-02T10:00:00Z","evidence_refs":[]}
  self.change("catalog/skills.json",edit)
  self.assertTrue(any("last_checked" in e for e in validate_repository(self.root)))
 def test_rejects_evidence_for_not_run_verification(self):
  def edit(d):
   d["skills"][0]["lifecycle"]="unverified"
   d["skills"][0]["selection"]["verification"]={"status":"not_run","evidence_refs":["tests/evidence/skill.json"]}
  self.change("catalog/skills.json",edit)
  errors=validate_repository(self.root)
  self.assertTrue(errors, "La verifica not_run ha accettato prove: " + repr(errors))


 def _add_material_with_license(self, license_record, include_evidence=True, evidence_result="passed"):
  evidence={
   "id":"proof.material.license.001",
   "subject":"material.source.matt.license",
   "result":evidence_result,
   "tested_at":"2026-11-03T20:00:00Z",
   "command":"Inspect LICENSE at the pinned source revision",
   "summary":"The declared license text was located and its obligations recorded. This is not a legal opinion."
  }
  if include_evidence:
   write_json(self.root,"tests/evidence/material-license.json",evidence)
  material={
   "id":"source.matt",
   "acquisition":{
    "status":"received",
    "acquired_at":"2026-11-03T20:00:00Z",
    "method":"remote reference registration",
    "original":{"kind":"remote_reference","uri":"https://github.com/mattpocock/skills"}
   },
   "classification":{"status":"classified","kind":"resource"},
   "documentation":{"status":"partial"},
   "verification":{"status":"not_verified"},
   "usability":{"status":"not_assessed"},
   "license":license_record
  }
  catalog=self.root/"catalog/materials.json"
  data=json.loads(catalog.read_text(encoding="utf-8"))
  data["materials"].append(material)
  catalog.write_text(json.dumps(data),encoding="utf-8")

 def test_accepts_reviewed_material_license_with_matching_evidence(self):
  license_record={
   "status":"identified",
   "identifier":"MIT",
   "source_uri":"https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/LICENSE",
   "source_revision":"4ae2317ddb22b046e26455e4f9c9b3aaaf62212d",
   "file_path":"LICENSE",
   "review_status":"reviewed",
   "reviewed_at":"2026-11-03T20:00:00Z",
   "evidence_refs":["tests/evidence/material-license.json"],
   "obligations":["Preserve the copyright notice and include the MIT license text."],
   "notes":["Review of the declared license text; not a legal opinion."]
  }
  self._add_material_with_license(license_record)
  self.assertEqual(validate_repository(self.root),[])

 def test_rejects_reviewed_material_license_without_evidence_file(self):
  license_record={
   "status":"identified",
   "identifier":"MIT",
   "source_uri":"https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/LICENSE",
   "source_revision":"4ae2317ddb22b046e26455e4f9c9b3aaaf62212d",
   "file_path":"LICENSE",
   "review_status":"reviewed",
   "reviewed_at":"2026-11-03T20:00:00Z",
   "evidence_refs":["tests/evidence/missing-license.json"],
   "obligations":[],
   "notes":[]
  }
  self._add_material_with_license(license_record,include_evidence=False)
  errors=validate_repository(self.root)
  self.assertTrue(any("prova non trovata" in e.lower() for e in errors),repr(errors))

 def test_rejects_identified_material_license_without_identifier(self):
  license_record={
   "status":"identified",
   "source_uri":"https://github.com/mattpocock/skills",
   "review_status":"not_reviewed",
   "evidence_refs":[]
  }
  self._add_material_with_license(license_record,include_evidence=False)
  self.assertTrue(any("identifier" in e.lower() for e in validate_repository(self.root)))

 
 def test_accepts_not_declared_license_after_review(self):
  license_record={
   "status":"not_declared",
   "source_uri":"https://github.com/example/project/tree/0123456789abcdef",
   "source_revision":"0123456789abcdef",
   "review_status":"reviewed",
   "reviewed_at":"2026-11-03T20:00:00Z",
   "evidence_refs":["tests/evidence/material-license.json"],
   "obligations":[],
   "notes":["La revisione della revisione esaminata non ha individuato una dichiarazione di licenza."]
  }
  self._add_material_with_license(license_record)
  self.assertEqual(validate_repository(self.root),[])

 def test_ambiguous_license_requires_inconclusive_evidence(self):
  license_record={
   "status":"ambiguous",
   "source_uri":"https://github.com/example/project/tree/0123456789abcdef",
   "source_revision":"0123456789abcdef",
   "review_status":"needs_human_review",
   "reviewed_at":"2026-11-03T20:00:00Z",
   "evidence_refs":["tests/evidence/material-license.json"],
   "obligations":[],
   "notes":["Le fonti presentano dichiarazioni discordanti; serve valutazione umana."]
  }
  self._add_material_with_license(license_record,evidence_result="passed")
  errors=validate_repository(self.root)
  self.assertTrue(any("inconclusive" in e.lower() for e in errors),repr(errors))

 def test_accepts_ambiguous_license_with_inconclusive_evidence(self):
  license_record={
   "status":"ambiguous",
   "source_uri":"https://github.com/example/project/tree/0123456789abcdef",
   "source_revision":"0123456789abcdef",
   "review_status":"needs_human_review",
   "reviewed_at":"2026-11-03T20:00:00Z",
   "evidence_refs":["tests/evidence/material-license.json"],
   "obligations":[],
   "notes":["Le fonti presentano dichiarazioni discordanti; serve valutazione umana."]
  }
  self._add_material_with_license(license_record,evidence_result="inconclusive")
  self.assertEqual(validate_repository(self.root),[])


 def test_accepts_skill_with_multiple_source_materials(self):
  materials=[
   {
    "id":"source.agent-skills-format",
    "acquisition":{"status":"received","acquired_at":"2026-11-03T20:00:00Z","method":"remote_reference","original":{"kind":"remote_reference","uri":"https://example.org/agent-skills"}},
    "classification":{"status":"classified","kind":"resource"},
    "documentation":{"status":"partial"},
    "verification":{"status":"not_verified"},
    "usability":{"status":"not_assessed"}
   },
   {
    "id":"source.unlazy-evidence-control",
    "acquisition":{"status":"received","acquired_at":"2026-11-03T20:00:00Z","method":"remote_reference","original":{"kind":"remote_reference","uri":"https://example.org/unlazy"}},
    "classification":{"status":"provisional","kind":"skill"},
    "documentation":{"status":"partial"},
    "verification":{"status":"not_verified"},
    "usability":{"status":"requires_adapter"}
   }
  ]
  write_json(self.root,"catalog/materials.json",{"catalog_version":"1.0","materials":materials})
  self.change("catalog/skills.json",lambda d:d["skills"][0].update(source_material_ids=["source.agent-skills-format","source.unlazy-evidence-control"]))
  self.assertEqual(validate_repository(self.root),[])

 def test_rejects_skill_with_missing_source_material(self):
  self.change("catalog/skills.json",lambda d:d["skills"][0].update(source_material_ids=["source.missing"]))
  errors=validate_repository(self.root)
  self.assertTrue(any("materiale di origine inesistente" in e.lower() for e in errors),repr(errors))

if __name__=="__main__":unittest.main()
