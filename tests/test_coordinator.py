import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.coordinator import PlanValidationError, validate_plan


NOW = "2026-11-03T21:00:00Z"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def evidence(evidence_id, subject):
    return {
        "id": evidence_id,
        "subject": subject,
        "result": "passed",
        "tested_at": NOW,
        "command": "Prova controllata del coordinatore.",
        "summary": "La prova di riferimento è stata eseguita e registrata."
    }


def make_valid_library(root, *, lifecycle="stable", risk_level="low", implementation_permissions=None,
                       implementation_tools=None):
    source_root = Path(__file__).resolve().parents[1]
    shutil.copytree(source_root / "schemas", root / "schemas")
    (root / "skills" / "read").mkdir(parents=True)
    (root / "skills" / "read" / "SKILL.md").write_text(
        "---\nname: read\ndescription: Read a file.\n---\n\n# Read a file\n",
        encoding="utf-8"
    )
    write_json(root / "tests" / "evidence" / "skill-read.json", evidence("proof.skill.read", "skill.read"))
    write_json(root / "tests" / "evidence" / "impl-read.json", evidence("proof.impl.read", "impl.read"))

    capability = {
        "id": "cap.read",
        "name": "Read file",
        "description": "Read a file and return its content.",
        "category": "file_access",
        "expected_result": "The file content is returned.",
        "verification_criteria": ["The returned content matches the source file."],
        "skill_ids": ["skill.read"],
        "status": "active"
    }
    skill = {
        "id": "skill.read",
        "path": "skills/read/SKILL.md",
        "capability_ids": ["cap.read"],
        "scope": "universal",
        "version": "1.0.0",
        "lifecycle": lifecycle,
        "tags": ["read"],
        "selection": {
            "task_signals": ["read a file"],
            "inputs": [{"name": "path", "description": "File path.", "required": True, "format": "path"}],
            "outputs": [{"name": "content", "description": "File content.", "format": "text"}],
            "prerequisites": [],
            "constraints": [],
            "risk_level": risk_level,
            "verification": {
                "status": "passed",
                "last_checked": NOW,
                "evidence_refs": ["tests/evidence/skill-read.json"]
            }
        }
    }
    implementation = {
        "id": "impl.read",
        "skill_id": "skill.read",
        "skill_version": "1.0.0",
        "platform": "python",
        "path": "implementations/test/1-0-0/manifest.json",
        "requirements": [],
        "tool_requirements": implementation_tools if implementation_tools is not None else ["file.read"],
        "permissions_required": implementation_permissions if implementation_permissions is not None else ["file.read"],
        "agent_compatibility": {"mode": "any", "agents": []},
        "status": "verified",
        "verification": {
            "status": "passed",
            "last_checked": NOW,
            "evidence_refs": ["tests/evidence/impl-read.json"]
        }
    }
    manifest = {
        "id": "impl.read",
        "skill_id": "skill.read",
        "skill_version": "1.0.0",
        "platform": "python",
        "entrypoint": "scripts/read_file.py"
    }
    write_json(root / "implementations" / "test" / "1-0-0" / "manifest.json", manifest)

    write_json(root / "catalog" / "materials.json", {"catalog_version": "1.0", "materials": []})
    write_json(root / "catalog" / "capabilities.json", {"catalog_version": "1.0", "capabilities": [capability]})
    write_json(root / "catalog" / "skills.json", {"catalog_version": "1.0", "skills": [skill]})
    write_json(root / "catalog" / "implementations.json", {"catalog_version": "1.0", "implementations": [implementation]})


def proposal(*, steps=None):
    return {
        "plan_id": "plan.read-file",
        "objective": "Read a file and verify the returned content.",
        "acceptance_criteria": ["The returned content matches the source file."],
        "steps": steps if steps is not None else [{
            "id": "step.read",
            "capability_id": "cap.read",
            "skill_id": "skill.read",
            "implementation_id": "impl.read",
            "inputs": {"path": "sample.txt"},
            "outputs": {"content": "text"},
            "depends_on": [],
            "verification": {
                "criteria": ["The returned content matches the source file."],
                "method": "Compare the returned content with the source."
            },
            "recovery": ["Check the path and permissions before retrying."],
            "requires_human_approval": False
        }],
        "completion_rule": "All acceptance criteria are verified and accepted."
    }


def runtime_context(**overrides):
    value = {
        "agent_id": "codex",
        "agent_version": "1.0.0",
        "available_tools": ["file.read"],
        "granted_permissions": ["file.read"],
        "approved_experimental_skill_ids": [],
        "approved_step_ids": [],
        "approval_required_permissions": ["file.delete", "system.install", "network.send"]
    }
    value.update(overrides)
    return value


class CoordinatorPlanValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        make_valid_library(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_plan_is_ready_without_execution(self):
        result = validate_plan(self.root, proposal(), runtime_context(), now=NOW)
        self.assertEqual(result["status"], "ready_for_execution")
        self.assertEqual(result["gaps"], [])
        self.assertEqual(result["steps"][0]["validation_status"], "ready")
        self.assertIn("skills_sha256", result["catalog_snapshot"])

    def test_missing_tool_and_permission_block_plan(self):
        result = validate_plan(
            self.root,
            proposal(),
            runtime_context(available_tools=[], granted_permissions=[]),
            now=NOW
        )
        gap_types = {gap["type"] for gap in result["gaps"]}
        self.assertEqual(result["status"], "blocked")
        self.assertIn("missing_tool", gap_types)
        self.assertIn("missing_authorization", gap_types)

    def test_dependency_cycle_blocks_plan(self):
        steps = proposal()["steps"]
        first = dict(steps[0], id="step.one", depends_on=["step.two"])
        second = dict(steps[0], id="step.two", depends_on=["step.one"])
        result = validate_plan(self.root, proposal(steps=[first, second]), runtime_context(), now=NOW)
        self.assertEqual(result["status"], "blocked")
        self.assertIn("dependency_cycle", {gap["type"] for gap in result["gaps"]})

    def test_experimental_skill_requires_explicit_approval(self):
        make_valid_library(self.root, lifecycle="experimental")
        result = validate_plan(self.root, proposal(), runtime_context(), now=NOW)
        self.assertEqual(result["status"], "awaiting_approval")
        self.assertIn("skill_requires_approval", {gap["type"] for gap in result["gaps"]})
        approved = validate_plan(
            self.root,
            proposal(),
            runtime_context(approved_experimental_skill_ids=["skill.read"]),
            now=NOW
        )
        self.assertEqual(approved["status"], "ready_for_execution")

    def test_high_risk_step_requires_approval_flag_and_human_approval(self):
        make_valid_library(
            self.root,
            risk_level="high",
            implementation_permissions=["file.delete"],
            implementation_tools=["file.delete"]
        )
        unflagged = validate_plan(self.root, proposal(), runtime_context(
            available_tools=["file.delete"], granted_permissions=["file.delete"]
        ), now=NOW)
        self.assertEqual(unflagged["status"], "blocked")
        self.assertIn("approval_flag_missing", {gap["type"] for gap in unflagged["gaps"]})

        steps = proposal()["steps"]
        steps[0]["requires_human_approval"] = True
        awaiting = validate_plan(self.root, proposal(steps=steps), runtime_context(
            available_tools=["file.delete"], granted_permissions=["file.delete"]
        ), now=NOW)
        self.assertEqual(awaiting["status"], "awaiting_approval")
        self.assertIn("human_approval_required", {gap["type"] for gap in awaiting["gaps"]})

        approved = validate_plan(self.root, proposal(steps=steps), runtime_context(
            available_tools=["file.delete"],
            granted_permissions=["file.delete"],
            approved_step_ids=["step.read"]
        ), now=NOW)
        self.assertEqual(approved["status"], "ready_for_execution")

    def test_invalid_proposal_is_rejected_at_boundary(self):
        invalid = proposal()
        invalid["unexpected"] = "not allowed"
        with self.assertRaises(PlanValidationError):
            validate_plan(self.root, invalid, runtime_context(), now=NOW)

    def test_current_library_catalogs_report_real_gaps(self):
        source_root = Path(__file__).resolve().parents[1]
        current_root = self.root / "current-library"
        for name in ("schemas", "catalog", "skills", "tests"):
            source = source_root / name
            if source.exists():
                shutil.copytree(source, current_root / name)
        plan = proposal()
        plan["steps"][0].update({
            "capability_id": "library.resource.discover-assess",
            "skill_id": "library.resource-discovery-assessment",
            "implementation_id": "implementation.not.present"
        })
        result = validate_plan(current_root, plan, runtime_context(), now=NOW)
        gap_types = {gap["type"] for gap in result["gaps"]}
        self.assertEqual(result["status"], "blocked")
        self.assertIn("capability_not_active", gap_types)
        self.assertIn("skill_not_verified", gap_types)
        self.assertIn("missing_implementation", gap_types)


if __name__ == "__main__":
    unittest.main()
