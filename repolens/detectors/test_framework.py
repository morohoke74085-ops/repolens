from __future__ import annotations

import json
import tomllib


def detect_test_frameworks(paths: set[str], manifests: dict[str, str], readme: str | None) -> list[str]:
    detected: list[str] = []

    pyproject_content = manifests.get("pyproject.toml")
    if pyproject_content:
        pyproject = tomllib.loads(pyproject_content)
        if pyproject.get("tool", {}).get("pytest") or _text_contains(pyproject_content, "pytest"):
            detected.append("pytest")

    if "pytest.ini" in paths or "tox.ini" in paths or any(path.endswith("conftest.py") for path in paths):
        detected.append("pytest")

    if any(path.startswith("tests/") and path.endswith(".py") for path in paths) and "pytest" not in detected:
        detected.append("unittest")

    package_json = manifests.get("package.json")
    if package_json:
        parsed = json.loads(package_json)
        scripts = parsed.get("scripts") or {}
        dependencies = {
            **(parsed.get("dependencies") or {}),
            **(parsed.get("devDependencies") or {}),
        }
        if "jest" in dependencies or any("jest" in str(value) for value in scripts.values()):
            detected.append("Jest")
        if "vitest" in dependencies or any("vitest" in str(value) for value in scripts.values()):
            detected.append("Vitest")

    if any(path.startswith("tests/") and path.endswith("_test.go") for path in paths):
        detected.append("go test")
    if "Cargo.toml" in paths and any(path.endswith("_test.rs") or "/tests/" in path for path in paths):
        detected.append("cargo test")

    if readme and _text_contains(readme, "pytest") and "pytest" not in detected:
        detected.append("pytest")

    return _unique(detected)


def _text_contains(text: str, needle: str) -> bool:
    return needle.lower() in text.lower()


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered

