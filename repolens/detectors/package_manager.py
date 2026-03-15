from __future__ import annotations

import json
import tomllib


def detect_package_managers(paths: set[str], manifests: dict[str, str]) -> list[str]:
    detected: list[str] = []

    if "pnpm-lock.yaml" in paths:
        detected.append("pnpm")
    if "yarn.lock" in paths:
        detected.append("Yarn")
    if "package-lock.json" in paths or ("package.json" in paths and not detected):
        detected.append("npm")

    if "Pipfile" in paths:
        detected.append("Pipenv")

    pyproject_content = manifests.get("pyproject.toml")
    if pyproject_content:
        pyproject = tomllib.loads(pyproject_content)
        if pyproject.get("tool", {}).get("poetry"):
            detected.append("Poetry")
        elif "pip" not in detected:
            detected.append("pip")
    elif "requirements.txt" in paths or "setup.py" in paths or "setup.cfg" in paths:
        detected.append("pip")

    if "Cargo.toml" in paths:
        detected.append("Cargo")
    if "go.mod" in paths:
        detected.append("Go modules")

    package_json = manifests.get("package.json")
    if package_json:
        parsed = json.loads(package_json)
        package_manager = parsed.get("packageManager")
        if isinstance(package_manager, str):
            if package_manager.startswith("pnpm@") and "pnpm" not in detected:
                detected.insert(0, "pnpm")
            if package_manager.startswith("yarn@") and "Yarn" not in detected:
                detected.insert(0, "Yarn")

    return _unique(detected)


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered

