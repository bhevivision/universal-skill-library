#!/usr/bin/env python3
"""Valuta l'estrazione semantica completa su materiali con fatti attesi."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.llama_cpp_adapter import LlamaCppServerAdapter
    from scripts.semantic_pipeline import classify_material
except ImportError:
    from llama_cpp_adapter import LlamaCppServerAdapter
    from semantic_pipeline import classify_material


def _field_text(proposal: dict, field: str) -> str:
    if field == "capabilities":
        values = []
        for item in proposal.get("capabilities", []):
            values.extend((item.get("name", ""), item.get("description", "")))
        return " ".join(values).lower()
    if field in {"inputs", "outputs", "usage_conditions"}:
        items = proposal.get("interfaces", {}).get(field, [])
        return " ".join(item.get("value", "") for item in items).lower()
    if field == "dependencies":
        return " ".join(item.get("name", "") for item in proposal.get("dependencies", [])).lower()
    if field == "tools_and_platforms":
        return " ".join(item.get("name", "") for item in proposal.get("tools_and_platforms", [])).lower()
    if field == "risks":
        return " ".join(item.get("description", "") for item in proposal.get("risks", [])).lower()
    raise ValueError(f"Campo di valutazione non supportato: {field}")


def match_expected_facts(expected: dict, proposal: dict) -> tuple[int, int, list[dict]]:
    """Confronta parole-chiave dichiarate con il campo semantico corrispondente."""
    matched = 0
    total = 0
    details = []
    for field, facts in expected.items():
        actual = _field_text(proposal, field)
        for fact in facts:
            if not isinstance(fact, list) or not fact or not all(isinstance(word, str) and word for word in fact):
                raise ValueError(f"Fatto atteso non valido nel campo {field}.")
            found = all(word.lower() in actual for word in fact)
            total += 1
            matched += int(found)
            details.append({"field": field, "keywords": fact, "matched": found})
    return matched, total, details


def score_extraction(rows: list[dict]) -> dict:
    total = len(rows)
    expected_facts = sum(row.get("expected_facts", 0) for row in rows)
    matched_facts = sum(row.get("matched_facts", 0) for row in rows)
    claims_total = sum(row.get("claims_total", 0) for row in rows)
    claims_with_evidence = sum(row.get("claims_with_evidence", 0) for row in rows)
    return {
        "sample_count": total,
        "kind_accuracy": round(
            sum(row.get("expected_kind") == row.get("predicted_kind") for row in rows) / total, 4
        ) if total else 0.0,
        "expected_fact_coverage": round(matched_facts / expected_facts, 4) if expected_facts else 0.0,
        "evidence_verification_rate": round(
            sum(bool(row.get("evidence_verified")) for row in rows) / total, 4
        ) if total else 0.0,
        "claim_evidence_coverage": round(
            claims_with_evidence / claims_total, 4
        ) if claims_total else 0.0,
        "completed_samples": sum(row.get("status") == "completed" for row in rows),
        "partial_samples": sum(row.get("status") == "partial" for row in rows),
        "failed_samples": sum(row.get("status") in {"failed", "not_available"} for row in rows),
        "mean_elapsed_seconds": round(
            sum(row.get("elapsed_seconds", 0) for row in rows) / total, 3
        ) if total else 0.0,
    }


def _claim_evidence_counts(proposal: dict) -> tuple[int, int]:
    claims = []
    classification = proposal.get("classification", {})
    if isinstance(classification, dict) and classification.get("kind") != "unclassified":
        claims.append(classification)
    claims.extend(proposal.get("capabilities", []))
    interfaces = proposal.get("interfaces", {})
    for field in ("inputs", "outputs", "usage_conditions"):
        claims.extend(interfaces.get(field, []))
    claims.extend(
        item for item in proposal.get("dependencies", [])
        if item.get("certainty") in {"declared", "inferred"}
    )
    claims.extend(proposal.get("tools_and_platforms", []))
    claims.extend(proposal.get("risks", []))
    claims.extend(proposal.get("contradictions", []))
    total = len(claims)
    with_evidence = sum(
        bool(item.get("evidence_refs"))
        and bool(item.get("evidence_quotes"))
        and all(isinstance(ref, str) and ref for ref in item.get("evidence_refs", []))
        and all(
            isinstance(quote, dict)
            and quote.get("evidence_ref") in item.get("evidence_refs", [])
            and isinstance(quote.get("quote"), str)
            and bool(quote["quote"].strip())
            for quote in item.get("evidence_quotes", [])
        )
        for item in claims
    )
    return total, with_evidence


def _create_sample_library(root: Path, sample: dict) -> tuple[str, str]:
    sample_id = sample["id"]
    material_id = "eval." + sample_id
    source = root / "intake" / ("acq-" + sample_id) / "source.md"
    source.parent.mkdir(parents=True)
    source.write_text(sample["text"], encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    record = {
        "id": material_id,
        "acquisition": {
            "status": "preserved",
            "acquired_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "method": "evaluation_fixture",
            "original": {
                "kind": "file",
                "path": source.relative_to(root).as_posix(),
                "sha256": digest,
                "digest_algorithm": "sha256-file-v1",
            },
        },
        "classification": {"status": "not_examined", "kind": "unclassified"},
        "documentation": {"status": "unknown"},
        "verification": {"status": "not_verified"},
        "usability": {"status": "not_assessed"},
    }
    catalog = root / "catalog" / "materials.json"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(
        json.dumps({"catalog_version": "1.0", "materials": [record]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return material_id, digest


def run_extraction_evaluation(adapter, dataset: dict, work_root: Path | None = None) -> dict:
    rows = []
    if work_root is not None:
        work_root = Path(work_root)
        work_root.mkdir(parents=True, exist_ok=True)

    for sample in dataset["samples"]:
        started = time.monotonic()
        row = {
            "id": sample["id"],
            "expected_kind": sample["expected_kind"],
            "predicted_kind": "unclassified",
            "status": "failed",
            "expected_facts": 0,
            "matched_facts": 0,
            "evidence_verified": False,
            "claims_total": 0,
            "claims_with_evidence": 0,
            "fact_details": [],
            "diagnostics": [],
            "error": None,
        }
        try:
            with tempfile.TemporaryDirectory(dir=str(work_root) if work_root else None) as temp:
                root = Path(temp)
                material_id, _ = _create_sample_library(root, sample)
                result = classify_material(
                    root,
                    material_id,
                    analyzer=adapter,
                    request_id="eval:" + sample["id"],
                )
                proposal = result.get("proposal") or {}
                row["status"] = result.get("status", "failed")
                row["predicted_kind"] = proposal.get("classification", {}).get("kind", "unclassified")
                row["evidence_verified"] = bool(result.get("evidence_verified"))
                row["diagnostics"] = list(proposal.get("limits", [])) + list(proposal.get("unknowns", []))
                matched, total, details = match_expected_facts(sample.get("expected_facts", {}), proposal)
                row["expected_facts"] = total
                row["matched_facts"] = matched
                row["fact_details"] = details
                row["claims_total"], row["claims_with_evidence"] = _claim_evidence_counts(proposal)
                if row["status"] not in {"completed", "partial"}:
                    row["error"] = "pipeline_status:" + str(row["status"])
                elif not row["evidence_verified"]:
                    row["error"] = "evidence_not_verified"
        except Exception as exc:
            row["error"] = type(exc).__name__ + ": " + str(exc)
        row["elapsed_seconds"] = round(time.monotonic() - started, 3)
        rows.append(row)

    return {
        "dataset_version": dataset.get("dataset_version", "unknown"),
        "metrics": score_extraction(rows),
        "predictions": rows,
        "interpretation": [
            "La copertura dei fatti confronta parole-chiave attese con i campi semantici corrispondenti; non sostituisce una revisione umana del significato.",
            "La verifica delle prove attesta la coerenza tecnica di percorsi e impronte rispetto ai materiali campione.",
            "La presenza di riferimenti alle prove non dimostra da sola che ogni affermazione sia semanticamente supportata dal passaggio corretto.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Valuta l'estrazione semantica completa con un modello GGUF locale.")
    parser.add_argument("base_url", nargs="?", default="http://127.0.0.1:8080")
    parser.add_argument("--dataset", type=Path, default=Path(__file__).resolve().parents[1] / "evaluation" / "semantic-extraction-samples.json")
    args = parser.parse_args()
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    adapter = LlamaCppServerAdapter(
        base_url=args.base_url,
        model="Qwen2.5-3B-Instruct-GGUF-Q4_K_M",
        timeout_seconds=120,
        max_response_bytes=2 * 1024 * 1024,
        max_tokens=1024,
        classification_only=False,
    )
    report = run_extraction_evaluation(adapter, dataset, work_root=Path(os.environ.get("TMPDIR", "/tmp")))
    report.update({
        "report_version": "1.0",
        "protocol_version": "1.0",
        "mode": "full_semantic_extraction",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "model": "Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M",
        "adapter": adapter.version,
        "dataset_sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
        "runtime_limits": {
            "context_tokens": 4096,
            "max_generated_tokens": 1024,
            "request_timeout_seconds": 120,
        },
        "evaluation_note": "Valutazione esplorativa dell'estrazione semantica completa; le etichette e i fatti attesi restano nel valutatore e non vengono inviati al modello.",
    })
    output = Path(os.environ.get("SEMANTIC_EXTRACTION_REPORT", "/tmp/semantic-extraction-evaluation-report.json"))
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    print("SEMANTIC_EXTRACTION_REPORT_B64=" + base64.b64encode(
        json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("ascii"), flush=True)
    return 0 if all(row["error"] is None for row in report["predictions"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
