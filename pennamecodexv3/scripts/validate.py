#!/usr/bin/env python3
"""Validate v3 JSON artifacts with the repository's dependency-free schema subset.

The v3 schemas intentionally use a small JSON Schema 2020-12 subset so a fresh
clone can validate packets without installing packages. Unsupported keywords
are annotations only; all structural keywords used by this repository are
implemented below.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


class ValidationError(Exception):
    pass


def _resolve_pointer(document: dict[str, Any], pointer: str) -> Any:
    if not pointer.startswith("#/"):
        raise ValidationError(f"unsupported reference: {pointer}")
    value: Any = document
    for raw_part in pointer[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        value = value[part]
    return value


def _matches_type(instance: Any, expected: str) -> bool:
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }
    return checks[expected](instance)


def validate_instance(
    instance: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any] | None = None,
    path: str = "$",
) -> list[str]:
    """Return every validation error found in *instance*."""
    root_schema = root_schema or schema
    errors: list[str] = []

    if "$ref" in schema:
        target = _resolve_pointer(root_schema, schema["$ref"])
        return validate_instance(instance, target, root_schema, path)

    if "oneOf" in schema:
        matches = [
            validate_instance(instance, candidate, root_schema, path)
            for candidate in schema["oneOf"]
        ]
        passing = [candidate_errors for candidate_errors in matches if not candidate_errors]
        if len(passing) != 1:
            errors.append(f"{path}: must match exactly one allowed shape")
        return errors

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(_matches_type(instance, item) for item in expected_types):
            errors.append(f"{path}: expected {' or '.join(expected_types)}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']!r}")

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key!r}")

        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], root_schema, f"{path}.{key}"))

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for index, value in enumerate(instance):
                errors.extend(validate_instance(value, item_schema, root_schema, f"{path}[{index}]"))
        if schema.get("uniqueItems"):
            serialized = [json.dumps(value, sort_keys=True) for value in instance]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: array items must be unique")

    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{path}: string does not match {schema['pattern']!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: value is below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: value exceeds maximum {schema['maximum']}")

    return errors


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path)
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()

    try:
        schema = load_json(args.schema)
        instance = load_json(args.instance)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = validate_instance(instance, schema)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"PASS {args.instance} against {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
