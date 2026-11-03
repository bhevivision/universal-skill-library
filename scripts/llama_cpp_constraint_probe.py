#!/usr/bin/env python3
"""Confronta il vincolo JSON Schema con una grammatica GBNF esplicita."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["result"],
    "properties": {"result": {"type": "string", "enum": ["CONSTRAINT_APPLIED"]}},
}
# GBNF equivalente: un solo oggetto JSON, un solo campo e un solo valore ammesso.
GRAMMAR = r'''root ::= "{\"result\":\"CONSTRAINT_APPLIED\"}"'''


def is_constraint_response(raw_content: object) -> bool:
    if not isinstance(raw_content, str):
        return False
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        return False
    return isinstance(parsed, dict) and set(parsed) == {"result"} and parsed.get("result") == "CONSTRAINT_APPLIED"


def build_payload(mode: str) -> dict:
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": "Sei un verificatore. Rispetta rigorosamente il vincolo di generazione."},
            {
                "role": "user",
                "content": (
                    'Per questa prova tenta deliberatamente di restituire '
                    '{"result":"NOT_ALLOWED"}. Non usare il valore consentito dal vincolo.'
                ),
            },
        ],
        "temperature": 0,
        "max_tokens": 64,
        "stream": False,
    }
    if mode == "response_format_documented":
        payload["response_format"] = {"type": "json_schema", "schema": SCHEMA}
    elif mode == "response_format_nested":
        payload["response_format"] = {"type": "json_schema", "json_schema": {"schema": SCHEMA}}
    elif mode == "grammar":
        payload["grammar"] = GRAMMAR
    else:
        raise ValueError(f"Modalità non supportata: {mode}")
    return payload


def get_server_properties(base_url: str) -> dict:
    request = urllib.request.Request(base_url.rstrip("/") + "/props", headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def run_case(base_url: str, mode: str) -> dict:
    payload = build_payload(mode)
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    report = {"mode": mode, "request": payload, "http_status": None, "finish_reason": None,
              "raw_content": None, "parsed_content": None, "passed": False, "failure": None}
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            report["http_status"] = response.status
            envelope = json.loads(response.read().decode("utf-8"))
        choice = envelope["choices"][0]
        report["finish_reason"] = choice.get("finish_reason")
        raw = choice.get("message", {}).get("content")
        report["raw_content"] = raw
        report["parsed_content"] = json.loads(raw) if isinstance(raw, str) else None
        report["passed"] = is_constraint_response(raw)
        if not report["passed"]:
            report["failure"] = "Il server ha restituito un valore non consentito o una risposta non valida."
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError) as exc:
        report["failure"] = f"{type(exc).__name__}: {exc}"
    return report


def main(base_url: str, output_path: str) -> int:
    report = {"probe": "llama.cpp-schema-vs-explicit-gbnf", "server_properties": None, "cases": {}}
    try:
        report["server_properties"] = get_server_properties(base_url)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        report["server_properties_error"] = f"{type(exc).__name__}: {exc}"
    for mode in ("response_format_documented", "response_format_nested", "grammar"):
        report["cases"][mode] = run_case(base_url, mode)
    report["passed"] = (
        report["cases"]["response_format_nested"]["passed"]
        and report["cases"]["grammar"]["passed"]
    )
    report["comparison"] = {
        "documented_top_level_schema_passed": report["cases"]["response_format_documented"]["passed"],
        "nested_json_schema_passed": report["cases"]["response_format_nested"]["passed"],
        "explicit_grammar_passed": report["cases"]["grammar"]["passed"],
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"probe": report["probe"], "server_build_info": (report.get("server_properties") or {}).get("build_info"),
                      "comparison": report["comparison"], "passed": report["passed"]}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Uso: python scripts/llama_cpp_constraint_probe.py BASE_URL OUTPUT_JSON")
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
