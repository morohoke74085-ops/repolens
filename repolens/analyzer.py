from __future__ import annotations

import json
import tomllib

from repolens.detectors.languages import detect_languages
from repolens.detectors.package_manager import detect_package_managers
from repolens.detectors.test_framework import detect_test_frameworks
from repolens.github_client import GitHubClient
from repolens.models import ProjectAnalysis, RepoFile


MANIFEST_CANDIDATES = [
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "pytest.ini",
    "tox.ini",
]

PREFERRED_DIRECTORIES = ["src", "app", "lib", "cmd", "pkg", "tests", "docs", "examples", "scripts"]


class RepoAnalyzer:
    def __init__(self, client: GitHubClient | None = None) -> None:
        self.client = client or GitHubClient()

    def analyze(self, repo_url: str) -> ProjectAnalysis:
        repo_ref = self.client.get_repo_ref(repo_url)
        metadata = self.client.get_repo_metadata(repo_ref)
        tree = self.client.get_tree(repo_ref, metadata.default_branch)
        readme = self.client.get_readme(repo_ref)

        file_paths = {item.path for item in tree if item.type == "blob"}
        directory_paths = {item.path for item in tree if item.type == "tree"}
        root_files = sorted(path for path in file_paths if "/" not in path)
        manifests = self._load_manifests(repo_ref, metadata.default_branch, file_paths)

        languages = detect_languages(file_paths, metadata.primary_language)
        package_managers = detect_package_managers(file_paths, manifests)
        test_frameworks = detect_test_frameworks(file_paths, manifests, readme)
        ci_providers = _detect_ci(file_paths)
        key_directories = _select_key_directories(directory_paths)
        entry_points = _derive_entry_points(file_paths, manifests, key_directories)
        install_steps = _derive_install_steps(package_managers, file_paths)
        run_steps = _derive_run_steps(package_managers, file_paths, manifests, key_directories)
        test_steps = _derive_test_steps(test_frameworks, package_managers, manifests)
        contribution_entry_points = _derive_contribution_ideas(file_paths, key_directories, test_frameworks)
        docs_gaps = _detect_docs_gaps(file_paths, directory_paths)
        tooling_gaps = _detect_tooling_gaps(file_paths, test_frameworks, ci_providers)
        summary = _build_summary(metadata.full_name, languages, package_managers, test_frameworks)

        return ProjectAnalysis(
            repo_ref=repo_ref,
            metadata=metadata,
            summary=summary,
            readme_excerpt=_summarize_readme(readme),
            root_files=root_files,
            manifest_files=[path for path in MANIFEST_CANDIDATES if path in file_paths],
            languages=languages,
            package_managers=package_managers,
            test_frameworks=test_frameworks,
            ci_providers=ci_providers,
            key_directories=key_directories,
            entry_points=entry_points,
            install_steps=install_steps,
            run_steps=run_steps,
            test_steps=test_steps,
            contribution_entry_points=contribution_entry_points,
            docs_gaps=docs_gaps,
            tooling_gaps=tooling_gaps,
        )

    def _load_manifests(self, repo_ref, branch: str, file_paths: set[str]) -> dict[str, str]:
        manifests: dict[str, str] = {}
        for path in MANIFEST_CANDIDATES:
            if path not in file_paths:
                continue
            content = self.client.get_file_content(repo_ref, path, branch)
            if content:
                manifests[path] = content
        return manifests


def _detect_ci(file_paths: set[str]) -> list[str]:
    providers: list[str] = []
    if any(path.startswith(".github/workflows/") for path in file_paths):
        providers.append("GitHub Actions")
    if ".gitlab-ci.yml" in file_paths:
        providers.append("GitLab CI")
    if any(path.startswith(".circleci/") for path in file_paths):
        providers.append("CircleCI")
    if "azure-pipelines.yml" in file_paths:
        providers.append("Azure Pipelines")
    return providers


def _select_key_directories(directory_paths: set[str]) -> list[str]:
    top_level = {path.split("/", maxsplit=1)[0] for path in directory_paths}
    ordered = [name for name in PREFERRED_DIRECTORIES if name in top_level]
    if ordered:
        return ordered
    return sorted(top_level)[:5]


def _derive_entry_points(
    file_paths: set[str],
    manifests: dict[str, str],
    key_directories: list[str],
) -> list[str]:
    points: list[str] = []

    if "package.json" in manifests:
        package_data = json.loads(manifests["package.json"])
        scripts = package_data.get("scripts") or {}
        if "start" in scripts:
            points.append("Check the `start` script in `package.json` for the primary runtime entry.")
        if "dev" in scripts:
            points.append("Inspect the `dev` script in `package.json` for the local development workflow.")
        main_entry = package_data.get("main")
        if isinstance(main_entry, str):
            points.append(f"Read `{main_entry}` as a likely JavaScript entry point.")

    if "pyproject.toml" in manifests:
        pyproject = tomllib.loads(manifests["pyproject.toml"])
        scripts = pyproject.get("project", {}).get("scripts") or {}
        if scripts:
            script_names = ", ".join(sorted(scripts))
            points.append(f"Review `pyproject.toml` script definitions: {script_names}.")

    for candidate in ["main.py", "app.py", "manage.py", "server.py", "index.js", "src/main.ts", "src/index.ts"]:
        if candidate in file_paths:
            points.append(f"Open `{candidate}` for a likely application starting point.")

    for directory in key_directories[:3]:
        points.append(f"Inspect `{directory}/` to understand the main project layout.")

    if "README.md" in file_paths:
        points.insert(0, "Read `README.md` first for setup context and repository intent.")

    return _unique(points)


def _derive_install_steps(package_managers: list[str], file_paths: set[str]) -> list[str]:
    steps: list[str] = []
    if "pnpm" in package_managers:
        steps.append("Run `pnpm install` to install dependencies.")
    elif "Yarn" in package_managers:
        steps.append("Run `yarn install` to install dependencies.")
    elif "npm" in package_managers:
        steps.append("Run `npm install` to install dependencies.")

    if "Poetry" in package_managers:
        steps.append("Run `poetry install` to create the environment and install dependencies.")
    elif "pip" in package_managers:
        if "requirements.txt" in file_paths:
            steps.append("Run `python -m pip install -r requirements.txt` to install Python dependencies.")
        if "pyproject.toml" in file_paths:
            steps.append("Run `python -m pip install -e .` for an editable local install.")

    if "Cargo" in package_managers:
        steps.append("Run `cargo build` to compile the project.")
    if "Go modules" in package_managers:
        steps.append("Run `go mod download` to fetch module dependencies.")

    if ".env.example" in file_paths:
        steps.append("Copy `.env.example` to `.env` and fill in required environment variables.")

    return _unique(steps)


def _derive_run_steps(
    package_managers: list[str],
    file_paths: set[str],
    manifests: dict[str, str],
    key_directories: list[str],
) -> list[str]:
    steps: list[str] = []

    package_json = manifests.get("package.json")
    if package_json:
        package_data = json.loads(package_json)
        scripts = package_data.get("scripts") or {}
        if "dev" in scripts:
            steps.append("Run `npm run dev` for the default development entry point.")
        if "start" in scripts:
            steps.append("Run `npm start` for the main runtime entry point.")

    if "pyproject.toml" in file_paths and "src" in key_directories:
        steps.append("Run `python -m <package>` after replacing `<package>` with the main Python package name.")
    for candidate in ["main.py", "app.py", "manage.py", "server.py"]:
        if candidate in file_paths:
            steps.append(f"Run `python {candidate}` for a likely local entry point.")

    if "Cargo" in package_managers:
        steps.append("Run `cargo run` for the default binary target.")
    if "Go modules" in package_managers and ("main.go" in file_paths or "cmd" in key_directories):
        steps.append("Run `go run .` or inspect `cmd/` for runnable binaries.")

    return _unique(steps)


def _derive_test_steps(
    test_frameworks: list[str],
    package_managers: list[str],
    manifests: dict[str, str],
) -> list[str]:
    steps: list[str] = []

    if "pytest" in test_frameworks:
        steps.append("Run `pytest` for the primary test suite.")
    if "unittest" in test_frameworks:
        steps.append("Run `python -m unittest` for built-in Python tests.")

    package_json = manifests.get("package.json")
    if package_json:
        package_data = json.loads(package_json)
        scripts = package_data.get("scripts") or {}
        if "test" in scripts:
            steps.append("Run `npm test` to execute the package test script.")
    if "Jest" in test_frameworks and not any("npm test" in step for step in steps):
        steps.append("Run `npx jest` to execute Jest tests.")
    if "Vitest" in test_frameworks and not any("npm test" in step for step in steps):
        steps.append("Run `npx vitest` to execute Vitest tests.")
    if "cargo test" in test_frameworks:
        steps.append("Run `cargo test` for Rust tests.")
    if "go test" in test_frameworks:
        steps.append("Run `go test ./...` for Go tests.")

    if not steps and "Cargo" in package_managers:
        steps.append("Run `cargo test` to discover Rust test coverage.")
    if not steps and "Go modules" in package_managers:
        steps.append("Run `go test ./...` to discover Go test coverage.")

    return _unique(steps)


def _derive_contribution_ideas(
    file_paths: set[str],
    key_directories: list[str],
    test_frameworks: list[str],
) -> list[str]:
    ideas: list[str] = []

    if "docs" in key_directories or "README.md" in file_paths:
        ideas.append("Improve onboarding docs, examples, and setup clarity.")
    if "tests" in key_directories or test_frameworks:
        ideas.append("Add or refine tests around high-value modules and edge cases.")
    if not test_frameworks:
        ideas.append("Set up a minimal automated test suite for safer contributions.")
    if "scripts" in key_directories:
        ideas.append("Document or simplify project scripts for contributor ergonomics.")
    if not any(path.startswith(".github/ISSUE_TEMPLATE/") for path in file_paths):
        ideas.append("Add GitHub issue templates to make triage easier.")
    if "examples" in key_directories:
        ideas.append("Expand runnable examples for first-time contributors.")

    return _unique(ideas)


def _detect_docs_gaps(file_paths: set[str], directory_paths: set[str]) -> list[str]:
    gaps: list[str] = []
    if "README.md" not in file_paths:
        gaps.append("Missing `README.md`.")
    if "CONTRIBUTING.md" not in file_paths:
        gaps.append("Missing `CONTRIBUTING.md` for contributor guidance.")
    if "LICENSE" not in file_paths:
        gaps.append("Missing a top-level `LICENSE` file.")
    if "docs" not in {path.split("/", maxsplit=1)[0] for path in directory_paths}:
        gaps.append("No dedicated `docs/` directory detected.")
    return gaps


def _detect_tooling_gaps(
    file_paths: set[str],
    test_frameworks: list[str],
    ci_providers: list[str],
) -> list[str]:
    gaps: list[str] = []
    if not test_frameworks:
        gaps.append("No obvious automated test framework was detected.")
    if not ci_providers:
        gaps.append("No CI workflow was detected.")
    if not any(path.startswith(".github/ISSUE_TEMPLATE/") for path in file_paths):
        gaps.append("No GitHub issue templates were detected.")
    if ".github/pull_request_template.md" not in file_paths:
        gaps.append("No GitHub pull request template was detected.")
    return gaps


def _build_summary(
    full_name: str,
    languages: list[str],
    package_managers: list[str],
    test_frameworks: list[str],
) -> str:
    language_text = ", ".join(languages) or "an unknown stack"
    package_manager_text = ", ".join(package_managers) or "an unknown package manager"
    test_text = ", ".join(test_frameworks) or "no obvious test framework"
    return (
        f"{full_name} looks like a {language_text} repository managed with "
        f"{package_manager_text}, with {test_text} detected."
    )


def _summarize_readme(readme: str | None) -> str | None:
    if not readme:
        return None
    stripped = " ".join(readme.split())
    return stripped[:240] + ("..." if len(stripped) > 240 else "")


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered

