#!/usr/bin/env python3
"""Confronto diagnostico A/B/C/D con conservazione progressiva delle risposte llama.cpp."""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from scripts.llama_cpp_adapter import (
    SYSTEM_PROMPT,
    LlamaCppServerAdapter,
    _normalize_full_evidence,
    _semantic_output_schema,
)
from scripts.semantic_claim_evidence import normalize_model_json
from scripts.semantic_extraction_evaluation import run_extraction_evaluation


CONFIGURATIONS = (
    {"id": "A", "description": "Schema attuale; nessun limite aggiunto agli array", "fix_pattern": False, "bound_arrays": False},
    {"id": "B", "description": "Schema attuale; array limitati a 6 elementi", "fix_pattern": False, "bound_arrays": True},
    {"id": "C", "description": "Pattern corretto; nessun limite aggiunto agli array", "fix_pattern": True, "bound_arrays": False},
    {"id": "D", "description": "Pattern corretto; array limitati a 6 elementi", "fix_pattern": True, "bound_arrays": True},
)


def consume_sse(lines, on_chunk, on_event=None):
    """Consuma eventi SSE e salva ogni frammento appena arriva."""
    pieces = []
    for raw_line in lines:
        line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
        line = line.strip()
        if not line or line.startswith(":") or not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            event = json.loads(data)
        except json.JSONDecodeError:
            continue
        if on_event is not None:\n            on_event(event)\n        choices = event.get("choices") or []
        if choices:
            delta = choices[0].get("delta") or {}
            fragment = delta.get("content")
            if isinstance(fragment, str) and fragment:
                pieces.append(fragment)
                on_chunk(fragment)
    return "".join(pieces)


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def _apply_configuration(schema, config):
    schema = copy.deepcopy(schema)

    def visit(value):
        if isinstance(value, dict):
            if config["fix_pattern"] and value.get("pattern") == r"^(intake/|catalog/materials\.json$)":
                value["pattern"] = r"^(intake/.*|catalog/materials\.json)$"
            if config["bound_arrays"] and value.get("type") == "array" and "maxItems" not in value:
                value["maxItems"] = 6
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(schema)
    return schema


class StreamingDiagnosticAdapter:
    """Adattatore limitato al test: non modifica l'adattatore di produzione."""

    def __init__(self, base_url, config, output_dir, timeout_seconds=180, max_tokens=2048):
        self.base_url = base_url.rstrip("/")
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = timeout_seconds
        self.max_tokens = max_tokens
        self.model = "Qwen2.5-3B-Instruct-GGUF-Q4_K_M"
        self.observations = []

    def analyze(self, request):
        request_id = str(request.get("request_id", "request-unknown"))
        safe_id = re.sub(r"[^A-Za-z0-9._-]", "-", request_id)
        stem = self.config["id"] + "-" + safe_id
        raw_path = self.output_dir / (stem + ".partial.txt")
        events_path = self.output_dir / (stem + ".events.jsonl")
        metrics = {
            "configuration": self.config["id"],
            "request_id": request_id,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "time_to_first_text_seconds": None,
            "generation_elapsed_seconds": None,
            "stream_chunks": 0,
            "generated_characters": 0,
            "completion_tokens": None,
            "finish_reason": None,
            "status": "started",
            "raw_response_file": raw_path.name,
            "events_file": events_path.name,
            "error": None,
        }
        self.observations.append(metrics)
        started = time.monotonic()
        first_text = [None]
        raw_path.write_text("", encoding="utf-8")
        model_request = dict(request)
        model_request["evidence_sources"] = [
            {"id": f"ev.sample-{index:03d}", "path": item.get("path"), "sha256": item.get("sha256")}
            for index, item in enumerate(request.get("selected_content", []), start=1)
            if isinstance(item, dict)
        ]
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(model_request, ensure_ascii=False, sort_keys=True)},
            ],
            "temperature": 0.1,
            "max_tokens": self.max_tokens,
            "stream": True,
            "stream_options": {"include_usage": True},
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": _apply_configuration(_semantic_output_schema(), self.config)},
            },
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = Request(
            self.base_url + "/v1/chat/completions",
            data=body,
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
            method="POST",
        )

        def observe_event(event):\n            usage = event.get("usage")\n            if isinstance(usage, dict):\n                value = usage.get("completion_tokens")\n                if isinstance(value, int) and value >= 0:\n                    metrics["completion_tokens"] = value\n            choices = event.get("choices") or []\n            if choices and choices[0].get("finish_reason") is not None:\n                metrics["finish_reason"] = choices[0].get("finish_reason")\n\n        def save_fragment(fragment):
            now = time.monotonic()
            if first_text[0] is None:
                first_text[0] = now
                metrics["time_to_first_text_seconds"] = round(now - started, 4)
            with raw_path.open("a", encoding="utf-8") as raw_file:
                raw_file.write(fragment)
                raw_file.flush()
                os.fsync(raw_file.fileno())
            metrics["stream_chunks"] += 1
            metrics["generated_characters"] += len(fragment)
            with events_path.open("a", encoding="utf-8") as event_file:
                event_file.write(json.dumps({
                    "elapsed_seconds": round(now - started, 4),
                    "chunk_number": metrics["stream_chunks"],
                    "characters": len(fragment),
                }) + "\n")
                event_file.flush()

        try:
            opener = build_opener(ProxyHandler({}), _NoRedirectHandler())
            with opener.open(http_request, timeout=self.timeout_seconds) as response:
                content = consume_sse(response, save_fragment, observe_event)
                # llama.cpp può includere usage nell'ultimo evento SSE; se presente viene
                # registrato dal parser dedicato nelle versioni server che lo supportano.
            metrics["status"] = "stream_completed"
            metrics["generation_elapsed_seconds"] = round(time.monotonic() - started, 4)
            if not content.strip():
                raise ValueError("Il flusso del modello è terminato senza testo.")
            parsed = normalize_model_json(content)
            if not isinstance(parsed, dict):
                raise ValueError("La risposta del modello non è un oggetto JSON.")
            metrics["status"] = "json_parsed"
            return _normalize_full_evidence(parsed, request)
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
            metrics["status"] = "interrupted_or_invalid"
            metrics["error"] = type(exc).__name__ + ": " + str(exc)[:1000]
            raise
        finally:
            metrics["generation_elapsed_seconds"] = round(time.monotonic() - started, 4)
            metrics["generated_characters"] = raw_path.stat().st_size if raw_path.exists() else 0
            (self.output_dir / (stem + ".metrics.json")).write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )


def run_comparison(base_url, dataset_path, output_dir, timeout_seconds=180, max_tokens=2048):
    import hashlib

    dataset_path = Path(dataset_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    comparison = {
        "report_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": "Qwen/Qwen2.5-3B-Instruct-GGUF:Q4_K_M",
        "dataset_sha256": hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
        "protocol": {
            "same_dataset": True,
            "same_model": True,
            "same_temperature": 0.1,
            "max_generated_tokens": max_tokens,
            "timeout_seconds": timeout_seconds,
            "runs_per_configuration": len(dataset["samples"]),
            "total_runs": len(CONFIGURATIONS) * len(dataset["samples"]),
        },
        "configurations": [],
        "interpretation": [
            "Il testo .partial.txt viene scritto e sincronizzato durante la generazione: resta disponibile anche in caso di timeout.",
            "completion_tokens è null se il server non comunica il conteggio token; non viene inventata una stima.",
            "La copertura dei fatti e le citazioni sono misure automatiche e richiedono revisione semantica.",
        ],
    }
    for config in CONFIGURATIONS:
        config_dir = output_dir / config["id"]
        adapter = StreamingDiagnosticAdapter(base_url, config, config_dir, timeout_seconds, max_tokens)
        report = run_extraction_evaluation(adapter, dataset, work_root=output_dir / "work")
        report["stream_observations"] = adapter.observations
        report["configuration"] = config
        report_path = config_dir / "evaluation-report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        comparison["configurations"].append({
            "id": config["id"],
            "description": config["description"],
            "metrics": report["metrics"],
            "stream_observations": adapter.observations,
            "report_file": str(report_path.relative_to(output_dir)),
        })
    (output_dir / "comparison-report.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return comparison


def main():
    parser = argparse.ArgumentParser(description="Confronta quattro configurazioni GGUF conservando le risposte progressive.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--dataset", type=Path, default=Path(__file__).resolve().parents[1] / "evaluation" / "semantic-extraction-samples.json")
    parser.add_argument("--output-dir", type=Path, default=Path("output/gguf-four-configs"))
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--max-tokens", type=int, default=2048)
    args = parser.parse_args()
    report = run_comparison(args.base_url, args.dataset, args.output_dir, args.timeout_seconds, args.max_tokens)
    print(json.dumps([
        {"configuration": item["id"], "metrics": item["metrics"]}
        for item in report["configurations"]
    ], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
