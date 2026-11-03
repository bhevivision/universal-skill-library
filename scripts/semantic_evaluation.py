#!/usr/bin/env python3
"""Valutazione ripetibile del classificatore semantico su campioni etichettati."""
from __future__ import annotations
import base64
import hashlib
import json
import os
import sys
import time
from pathlib import Path

try:
    from scripts.llama_cpp_adapter import LlamaCppServerAdapter
except ImportError:
    from llama_cpp_adapter import LlamaCppServerAdapter

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation" / "semantic-classification-samples.json"
KINDS = ("skill", "tool", "agent", "workflow", "resource", "composite", "unclassified")


def build_request(sample: dict) -> dict:
    raw = sample["text"].encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    source = f"intake/evaluation/{sample['id']}.md"
    return {
        "contract_version": "1.0",
        "request_id": f"eval:{sample['id']}",
        "material": {"id": f"eval.{sample['id']}", "sha256": digest, "original_kind": "file"},
        "files": [{"path": source, "sha256": digest, "size_bytes": len(raw)}],
        "selected_content": [{"path": source, "sha256": digest, "size_bytes": len(raw), "text": sample["text"]}],
        "limits": {"max_files": 1, "max_file_bytes": 262144, "max_total_bytes": 262144, "max_duration_seconds": 120},
        "safety": {
            "content_is_untrusted_data": True, "follow_instructions_in_content": False,
            "allow_filesystem_access": False, "allow_network_access": False,
            "allow_process_execution": False, "allow_credential_access": False,
            "allow_catalog_writes": False,
        },
    }


def score_predictions(rows: list[dict]) -> dict:
    labels = sorted({row["expected"] for row in rows} | {row["predicted"] for row in rows})
    total = len(rows)
    correct = sum(row["expected"] == row["predicted"] for row in rows)
    per_class = {}
    f1_values = []
    for label in labels:
        tp = sum(r["expected"] == label and r["predicted"] == label for r in rows)
        fp = sum(r["expected"] != label and r["predicted"] == label for r in rows)
        fn = sum(r["expected"] == label and r["predicted"] != label for r in rows)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        support = sum(r["expected"] == label for r in rows)
        per_class[label] = {"support": support, "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
        if support:
            f1_values.append(f1)
    classified = [row for row in rows if row["predicted"] != "unclassified"]
    return {
        "sample_count": total,
        "exact_accuracy": round(correct / total, 4) if total else 0.0,
        "coverage": round(len(classified) / total, 4) if total else 0.0,
        "selective_accuracy": round(
            sum(row["expected"] == row["predicted"] for row in classified) / len(classified), 4
        ) if classified else 0.0,
        "macro_f1": round(sum(f1_values) / len(f1_values), 4) if f1_values else 0.0,
        "per_class": per_class,
        "evidence_fidelity": round(sum(bool(row["evidence_valid"]) for row in rows) / total, 4) if total else 0.0,
        "abstention_count": sum(row["predicted"] == "unclassified" for row in rows),
        "mean_elapsed_seconds": round(sum(row.get("elapsed_seconds", 0) for row in rows) / total, 3) if total else 0.0,
    }


def run_evaluation(adapter, dataset: dict) -> dict:
    rows = []
    for sample in dataset["samples"]:
        started = time.monotonic()
        request = build_request(sample)
        error = None
        evidence_valid = False
        try:
            result = adapter.analyze(request)
            classification = result.get("classification")
            classification = classification if isinstance(classification, dict) else {}
            predicted = classification.get("kind", "unclassified")
            evidence = {
                item.get("id"): item
                for item in result.get("evidence", [])
                if isinstance(item, dict)
            }
            refs = classification.get("evidence_refs", [])
            source, digest = request["files"][0]["path"], request["files"][0]["sha256"]
            evidence_valid = bool(refs) and all(
                ref in evidence
                and evidence[ref].get("source") == source
                and evidence[ref].get("sha256") == digest
                and evidence[ref].get("kind") == "text_file"
                for ref in refs
            )
            if predicted not in KINDS:
                predicted = "unclassified"
            model_status = result.get("status")
            classification_diagnostics = {
                key: classification.get(key)
                for key in ("kind", "confidence", "rationale", "summary", "evidence_refs")
            }
            returned_keys = sorted(result.keys())
        except Exception as exc:
            predicted = "unclassified"
            model_status = "adapter_error"
            classification_diagnostics = {}
            returned_keys = []
            error = type(exc).__name__ + ": " + str(exc)
        rows.append({
            "id": sample["id"], "expected": sample["expected_kind"], "predicted": predicted,
            "correct": predicted == sample["expected_kind"], "evidence_valid": evidence_valid,
            "model_status": model_status, "classification": classification_diagnostics,
            "returned_keys": returned_keys,
            "elapsed_seconds": round(time.monotonic() - started, 3), "error": error,
        })
    return {"metrics": score_predictions(rows), "predictions": rows}


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    adapter = LlamaCppServerAdapter(base_url=base_url, model="Qwen2.5-0.5B-Instruct-GGUF-Q4_K_M", timeout_seconds=120, max_response_bytes=2 * 1024 * 1024, max_tokens=1024)
    report = run_evaluation(adapter, dataset)
    report.update({
        "dataset_version": dataset["dataset_version"],
        "model": "Qwen/Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M",
        "adapter": adapter.version,
        "evaluation_note": "Campione iniziale esplorativo, non una certificazione statistica. Le etichette attese non sono incluse nelle richieste inviate al modello.",
    })
    output = Path(os.environ.get("SEMANTIC_EVALUATION_REPORT", ROOT / "semantic-evaluation-report.json"))
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["metrics"], ensure_ascii=False, indent=2))
    print(f"Rapporto completo: {output}")
    encoded_report = base64.b64encode(
        json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    print("SEMANTIC_EVALUATION_REPORT_B64=" + encoded_report, flush=True)
    return 0 if all(row["error"] is None for row in report["predictions"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
