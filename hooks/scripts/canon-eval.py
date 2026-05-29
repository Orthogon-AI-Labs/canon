#!/usr/bin/env python3
"""Run a small canon skill eval file."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


class EvalError(Exception):
    pass


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)

    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise EvalError(
            "YAML eval files require PyYAML in this alpha runner. "
            "Install PyYAML or use a JSON eval file with the same structure."
        ) from exc

    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise EvalError("eval file must contain a mapping at the top level")
    return data


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return Path.cwd()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def read_text(root: Path, path_value: str | None) -> str:
    if not path_value:
        return ""
    path = Path(path_value)
    if not path.is_absolute():
        path = root / path
    return path.read_text(encoding="utf-8")


def command_output(command: str, root: Path, skill_path: str | None, input_path: str | None) -> tuple[str, str]:
    env = {
        "CANON_SKILL": skill_path or "",
        "CANON_INPUT": input_path or "",
    }
    result = subprocess.run(
        command,
        cwd=root,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **env},
        check=False,
    )
    return result.stdout, result.stderr


def validate_json_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    failures: list[str] = []
    expected_type = schema.get("type")

    if expected_type == "object" and not isinstance(value, dict):
        return [f"{path}: expected object"]
    if expected_type == "array" and not isinstance(value, list):
        return [f"{path}: expected array"]
    if expected_type == "string" and not isinstance(value, str):
        return [f"{path}: expected string"]
    if expected_type == "number" and not isinstance(value, (int, float)):
        return [f"{path}: expected number"]
    if expected_type == "boolean" and not isinstance(value, bool):
        return [f"{path}: expected boolean"]

    if isinstance(value, dict):
        for key in schema.get("required", []) or []:
            if key not in value:
                failures.append(f"{path}: missing required key {key}")
        properties = schema.get("properties") or {}
        if isinstance(properties, dict):
            for key, subschema in properties.items():
                if key in value and isinstance(subschema, dict):
                    failures.extend(validate_json_schema(value[key], subschema, f"{path}.{key}"))

    return failures


def grade_task(root: Path, skill_path: str | None, task: dict[str, Any]) -> tuple[bool, list[str]]:
    task_id = task.get("id", "<unnamed>")
    input_path = task.get("input")
    expected = task.get("expected") or {}
    if not isinstance(expected, dict):
        return False, [f"{task_id}: expected must be a mapping"]

    failures: list[str] = []
    if "command" in expected:
        text, stderr = command_output(str(expected["command"]), root, skill_path, input_path)
        if stderr.strip():
            failures.append(f"{task_id}: command wrote stderr: {stderr.strip()}")
    else:
        try:
            text = read_text(root, input_path)
        except FileNotFoundError:
            return False, [f"{task_id}: input file not found: {input_path}"]

    for needle in as_list(expected.get("contains")):
        if str(needle) not in text:
            failures.append(f'{task_id}: missing required text "{needle}"')

    for needle in as_list(expected.get("not_contains")):
        if str(needle) in text:
            failures.append(f'{task_id}: found forbidden text "{needle}"')

    for pattern in as_list(expected.get("regex")):
        if re.search(str(pattern), text, flags=re.MULTILINE) is None:
            failures.append(f'{task_id}: regex did not match "{pattern}"')

    if "json_schema" in expected:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            failures.append(f"{task_id}: output is not valid JSON: {exc}")
        else:
            schema = expected["json_schema"]
            if not isinstance(schema, dict):
                failures.append(f"{task_id}: json_schema must be a mapping")
            else:
                failures.extend(f"{task_id}: {failure}" for failure in validate_json_schema(parsed, schema))

    # Deterministic size budget. Used by `canon optimize <context-file>` to prove
    # a prune cut cost (char count is a stable, dependency-free proxy for tokens).
    # Pair with a `command` that runs the project's own tests to confirm behavior held.
    if "max_chars" in expected:
        limit = expected["max_chars"]
        if not isinstance(limit, int) or isinstance(limit, bool):
            failures.append(f"{task_id}: max_chars must be an integer")
        elif len(text) > limit:
            failures.append(f"{task_id}: output is {len(text)} chars, over max_chars {limit}")

    if "min_chars" in expected:
        floor = expected["min_chars"]
        if not isinstance(floor, int) or isinstance(floor, bool):
            failures.append(f"{task_id}: min_chars must be an integer")
        elif len(text) < floor:
            failures.append(f"{task_id}: output is {len(text)} chars, under min_chars {floor}")

    return len(failures) == 0, failures


def run_eval(path: Path) -> int:
    root = repo_root()
    data = load_yaml_or_json(path)
    tasks = data.get("tasks") or []
    if not isinstance(tasks, list):
        raise EvalError("tasks must be a list")

    skill_path = data.get("skill")
    passed = 0
    failures_by_task: list[str] = []

    print(f"[canon eval] {data.get('name', path.stem)}")
    for task in tasks:
        if not isinstance(task, dict):
            failures_by_task.append("<invalid>: task must be a mapping")
            continue
        ok, failures = grade_task(root, skill_path, task)
        task_id = task.get("id", "<unnamed>")
        if ok:
            passed += 1
            print(f"ok: {task_id}")
        else:
            print(f"fail: {task_id}")
            failures_by_task.extend(failures)

    total = len(tasks)
    print(f"score: {passed}/{total}")
    if failures_by_task:
        print()
        print("Failures:")
        for failure in failures_by_task:
            print(f"- {failure}")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a canon alpha eval file.")
    parser.add_argument("eval_file", help="Path to eval YAML or JSON file.")
    args = parser.parse_args()

    try:
        return run_eval(Path(args.eval_file))
    except EvalError as exc:
        print(f"[canon eval] error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
