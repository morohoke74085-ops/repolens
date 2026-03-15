from __future__ import annotations


LANGUAGE_PATTERNS: dict[str, tuple[str, ...]] = {
    "Python": (".py", "pyproject.toml", "requirements.txt", "setup.py"),
    "TypeScript": (".ts", ".tsx"),
    "JavaScript": (".js", ".jsx", "package.json"),
    "Go": (".go", "go.mod"),
    "Rust": (".rs", "Cargo.toml"),
}


def detect_languages(paths: set[str], primary_language: str | None = None) -> list[str]:
    detected: list[str] = []

    if primary_language:
        detected.append(primary_language)

    for language, patterns in LANGUAGE_PATTERNS.items():
        if language in detected:
            continue
        if any(_matches_pattern(path, patterns) for path in paths):
            detected.append(language)

    return detected


def _matches_pattern(path: str, patterns: tuple[str, ...]) -> bool:
    filename = path.rsplit("/", maxsplit=1)[-1]
    return any(path.endswith(pattern) or filename == pattern for pattern in patterns)

